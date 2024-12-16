import uuid
import logging
from typing import Optional, Dict, Tuple, Union, Literal, Any
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import httpx

from storage import storage_service # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class UploadRequest(BaseModel):
    project_id: Optional[str] = None
    content_type: Optional[str] = None
    thread_id: Optional[str] = None
    file_name: str

class UploadResponse(BaseModel):
    object_key: Optional[str]
    url: Optional[str]

@router.get("/")
def index():
    return {"message": "Hello, World!"}

@router.post("/upload", response_model=UploadResponse)
async def upload(
    request: Request,
    file: UploadFile = File(...),
    thread_id: Optional[str] = Form(None),
    mime: str = Form(default="application/octet-stream")
) -> Dict[str, Optional[str]]:
    # Hint towards limits on upload size
    """
    Handle file uploads with the following steps:
    1. Generate a unique ID for the file
    2. Get signed URL for upload
    3. Upload the file to storage
    4. Return the object key and signed URL
    """
    try:
        # Generate unique ID for the file
        file_id = str(uuid.uuid4())
        
        # Prepare request body for getting signed URL
        body = {
            "file_name": file_id,
            "contentType": mime or file.content_type,
            "threadId": thread_id
        }
        print(f"Request body: {body}")

        # Read file content
        content = await file.read()

        # Get signed URL and upload details
        async with httpx.AsyncClient(follow_redirects=True) as client:
            print(f"URL to uplaod file: {request.base_url}upload-file")
            response = await client.post(
                f"{request.base_url}upload-file",
                json=body,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code >= 400:
                logger.error(f"Failed to sign upload url: {response.text}")
                return {"object_key": None, "url": None}
            
            json_res = response.json()

        # Determine upload method and get upload details
        method = "put" if "put" in json_res else "post"
        request_dict: Dict[str, Any] = json_res.get(method, {})
        url: Optional[str] = request_dict.get("url")

        if not url:
            raise HTTPException(status_code=400, detail="Invalid server response")

        headers: Optional[Dict] = request_dict.get("headers")
        fields: Dict = request_dict.get("fields", {})
        object_key: Optional[str] = fields.get("key")
        upload_type: Literal["raw", "multipart"] = request_dict.get("uploadType", "multipart")
        signed_url: Optional[str] = json_res.get("signedUrl")

        # Prepare form data for multipart upload
        form_data = {} # type: Dict[str, Union[Tuple[Union[str, None], Any], Tuple[Union[str, None], Any, Any]]]
        for field_name, field_value in fields.items():
            form_data[field_name] = (None, field_value)

        # Add file to form data
        # Note: The content_type parameter is not needed here, as the correct MIME type should be set
        # in the 'Content-Type' field from upload_details
        form_data["file"] = (file_id, content, mime)

        print(f"Upload details: {json_res}")
        # Perform the upload
        async with httpx.AsyncClient(follow_redirects=True) as client:
            if upload_type == "raw":
                upload_response = await client.request(
                    url=url,
                    headers=headers,
                    method=method,
                    data=content, # type: ignore
                )
            else:
                upload_response = await client.request(
                    url=url,
                    headers=headers,
                    method=method,
                    files=form_data,
                )

            try:
                upload_response.raise_for_status()
                return {"object_key": object_key, "url": signed_url}
            except Exception as e:
                logger.error(f"Failed to upload file: {str(e)}")
                return {"object_key": None, "url": None}

    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-file")
async def upload_file(request: UploadRequest):
    try:
        prefix = f"projects/{request.project_id}" if request.project_id else "projects"
        if request.thread_id:
            prefix += f"/threads/{request.thread_id}"
        prefix += "/files"
        key = f"{prefix}/{request.file_name}"

        response = await storage_service.create_request(
            prefix=prefix,
            key=key,
            content_type=request.content_type
        )

        signed_url = await storage_service.sign_url(key)

        return {**response, "signed_url": signed_url}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))