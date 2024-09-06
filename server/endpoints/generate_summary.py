from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from server.utils.comman import generate_financial_summary


summary_router = APIRouter()


@summary_router.post("/generate-summary")
async def generate_summary(files: UploadFile = File(...)):

    try:
        if not files.file:
            raise HTTPException(status_code=400, detail="No file uploaded")
        
        analysis = await generate_financial_summary(files)
        if not analysis:
            raise HTTPException(status_code=400, detail="Error in generating summary")

        overall_summary = analysis[-1]
        if overall_summary:

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": {
                        "concise_summary": overall_summary.get("concise_analysis"),
                        "detailed_summary": overall_summary.get("detailed_analysis"),
                    },
                    "error": None,
                    "message": "Summary generated successfully.",
                },
            )
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "data": None,
                "error": str(e),
                "message": "Something went wrong!",
            },
        )
