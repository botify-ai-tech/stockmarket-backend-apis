import json
import re
from fastapi import APIRouter, File, HTTPException, UploadFile, Depends, BackgroundTasks
from fastapi.responses import JSONResponse

from server import crud, schemas
from server.utils.auth import get_current_user
from server.utils.comman import generate_financial_summary
from sqlalchemy.orm import Session
from server.endpoints.deps import get_db
from server.utils.pinecone import PineconeExecute


summary_router = APIRouter()
STATIC_FOLDER = "static"


def regex(data):
    pattern = r'"text":\s*"([^"]+)"'
    text_values = re.findall(pattern, data)
    full_text = (
        "\n".join(text_values)
        .replace("\\n", "\n")
        .replace("\\u20b9", "₹")
        .replace("\\u00a3", "£")
    )

    return full_text


@summary_router.post("/generate-summary")
async def generate_summary(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):

    try:
        if not file.file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        user_id = current_user.id
        analysis = await generate_financial_summary(file, user_id, background_tasks)
        if not analysis:
            raise HTTPException(status_code=400, detail="Error in generating summary")

        overall_summary = analysis[-1]
        if overall_summary:

            concise = overall_summary.get("concise_analysis")
            concise_analysis = regex(concise)

            detailed = overall_summary.get("detailed_analysis")
            detailed_analysis = regex(detailed)

            data = {
                "concise_analysis": concise_analysis,
                "detailed_analysis": detailed_analysis,
            }

            crud.summary.create(
                db,
                obj_in=schemas.CreateSummary(
                    user_id=current_user.id,
                    summary=data,
                    filename=file.filename,
                ),
            )

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": data,
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


@summary_router.post("/chat")
async def summary_chat(
    request: schemas.Query,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user.id
    query_text = request.question
    if not query_text:
        raise HTTPException(status_code=400, detail="Query text is required")

    pine_cone = PineconeExecute(user_id=user_id, texts=query_text)
    query_embedding = pine_cone.embed_text_with_retries()
    if not query_embedding:
        raise HTTPException(
            status_code=500, detail="Failed to generate query embedding"
        )

    results = pine_cone.search_in_pinecone(query_embedding=query_embedding)
    if not results:
        raise HTTPException(status_code=404, detail="No relevant information found")

    content = " ".join([res["metadata"]["text"] for res in results])

    answer = pine_cone.construct_prompt(content=content, question=query_text)

    crud.chat.create(
        db,
        obj_in=schemas.CreateChat(user_id=user_id, question=query_text, answer=answer),
    )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": answer,
            "error": None,
            "message": "Bot answer generated successfully.",
        },
    )


@summary_router.post("/chat-history")
async def summary_chat(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    chat_historys = crud.chat.get_chat_history(db, current_user.id)

    history = sorted(chat_historys, key=lambda x: x.created_at)

    history_list = []
    for chat in history:
        history_list.append(
            {
                "id": chat.id,
                "user_id": chat.user_id,
                "question": chat.question,
                "answer": chat.answer,
                "created_at": str(chat.created_at),
            }
        )

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": history_list,
            "error": None,
            "message": "Chat hostory fetched successfully.",
        },
    )
