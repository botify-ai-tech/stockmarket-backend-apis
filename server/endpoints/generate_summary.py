import uuid
import regex as re
from typing import Optional
from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
    Depends,
    BackgroundTasks,
)
from fastapi.responses import JSONResponse

from server import crud, schemas
from server.utils.auth import get_current_user
from server.utils.summary import generate_financial_summary
from server.utils.youtube import generate_youtube_summary
from server.utils.concall import generate_concall_summary
from sqlalchemy.orm import Session
from server.endpoints.deps import get_db
from server.utils.pinecone import PineconeExecute
from collections import defaultdict


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


@summary_router.post("/chat-history")
async def summary_chat(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        chat_historys = crud.chat.get_chat_history(db, current_user.id)
        history = sorted(chat_historys, key=lambda x: x.created_at)

        history_dict = defaultdict(list)

        for chat in history:
            history_dict[chat.session_id].append(
                {
                    "id": chat.id,
                    "user_id": chat.user_id,
                    "session_id": chat.session_id,
                    "question": chat.question,
                    "answer": chat.answer,
                    "filename": chat.filename,
                    "url": chat.url,
                    "content_topic": chat.content_topic,
                    "created_at": str(chat.created_at),
                }
            )

        # Convert dictionary to a list of session-based histories
        history_list = [
            {"session_id": session_id, "chats": chats}
            for session_id, chats in history_dict.items()
        ]

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": history_list,
                "error": None,
                "message": "Chat history fetched successfully.",
            },
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )
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


@summary_router.post("/chat-history-by-session")
async def summary_chat(
    data: schemas.ChatHistory,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        if data.session_id:
            chat_historys = crud.chat.get_chat_history_by_session_id(
                db, current_user.id, data.session_id
            )

        history = sorted(chat_historys, key=lambda x: x.created_at)

        history_list = []
        for chat in history:
            history_list.append(
                {
                    "id": chat.id,
                    "user_id": chat.user_id,
                    "session_id": chat.session_id,
                    "question": chat.question,
                    "answer": chat.answer,
                    "filename": chat.filename,
                    "url": chat.url,
                    "content_topic": chat.content_topic,
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

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )
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
async def general_chat(
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    question: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session_id: Optional[str] = Form(None),
    content_topic: Optional[str] = Form(None),
):
    try:
        if not session_id:
            session_id = str(uuid.uuid4())

        if (question and url) or (question and file):
            raise HTTPException(
                status_code=400,
                detail="Please sent any one 'file' or 'url' or 'question'.",
            )

        if not question:
            if file and url:
                raise HTTPException(
                    status_code=400, detail="Please sent any one 'file' or 'url'."
                )
            user_id = current_user.id
            analysis = await generate_financial_summary(
                file, url, user_id, background_tasks
            )
            if not analysis:
                raise HTTPException(
                    status_code=400, detail="Error in generating summary"
                )
            if analysis:
                detailed = analysis[0].get("detailed_analysis")
                detailed_analysis = regex(detailed)

                chat_ = crud.chat.create(
                    db,
                    obj_in=schemas.CreateChat(
                        user_id=current_user.id,
                        answer=detailed,
                        filename=file.filename if file else None,
                        url=url if url else None,
                        session_id=session_id,
                        content_topic=content_topic,
                    ),
                )

                response = {
                    "id": chat_.id,
                    "user_id": chat_.user_id,
                    "question": chat_.question,
                    "answer": chat_.answer,
                    "filename": chat_.filename,
                    "url": chat_.url,
                    "session_id": chat_.session_id,
                    "content_topic": chat_.content_topic,
                    "created_at": str(chat_.created_at),
                }

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "data": response,
                        "error": None,
                        "message": "Bot answer generated successfully.",
                    },
                )

        else:
            user_id = current_user.id
            query_text = question
            if not query_text:
                raise HTTPException(status_code=400, detail="Query text is required")

            pine_cone = PineconeExecute(user_id=user_id, texts=query_text)
            query_embedding = pine_cone.embed_text_with_retries(text=query_text)
            if not query_embedding:
                raise HTTPException(
                    status_code=500, detail="Failed to generate query embedding"
                )

            results = pine_cone.search_in_pinecone(query_embedding=query_embedding)

            content = (
                " ".join([res["metadata"]["text"] for res in results])
                if results
                else []
            )

            if content:
                answer = pine_cone.construct_prompt(
                    content=content, question=query_text
                )
            else:
                answer = (
                    "No relevant information found Please provied the valide details."
                )

            chat_ = crud.chat.create(
                db,
                obj_in=schemas.CreateChat(
                    user_id=user_id,
                    question=query_text,
                    answer=answer,
                    session_id=session_id,
                    content_topic=content_topic,
                ),
            )

            response = {
                "id": chat_.id,
                "user_id": chat_.user_id,
                "question": chat_.question,
                "answer": chat_.answer,
                "filename": chat_.filename,
                "url": chat_.url,
                "session_id": chat_.session_id,
                "content_topic": chat_.content_topic,
                "created_at": str(chat_.created_at),
            }

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": response,
                    "error": None,
                    "message": "Bot answer generated successfully.",
                },
            )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )
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
    

@summary_router.post("/concall")
async def general_chat(
    url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    question: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session_id: Optional[str] = Form(None),
    content_topic: Optional[str] = Form(None),
):
    try:
        if not session_id:
            session_id = str(uuid.uuid4())

        if (question and url) or (question and file):
            raise HTTPException(
                status_code=400,
                detail="Please sent any one 'file' or 'url' or 'question'.",
            )

        if not question:
            if file and url:
                raise HTTPException(
                    status_code=400, detail="Please sent any one 'file' or 'url'."
                )
            user_id = current_user.id
            analysis = await generate_concall_summary(
                file, url, user_id, background_tasks
            )
            if not analysis:
                raise HTTPException(
                    status_code=400, detail="Error in generating summary"
                )
            if analysis:
                detailed = analysis[0].get("detailed_analysis")
                detailed_analysis = regex(detailed)

                chat_ = crud.chat.create(
                    db,
                    obj_in=schemas.CreateChat(
                        user_id=current_user.id,
                        answer=detailed,
                        filename=file.filename if file else None,
                        url=url if url else None,
                        session_id=session_id,
                        content_topic=content_topic,
                    ),
                )

                response = {
                    "id": chat_.id,
                    "user_id": chat_.user_id,
                    "question": chat_.question,
                    "answer": chat_.answer,
                    "filename": chat_.filename,
                    "url": chat_.url,
                    "session_id": chat_.session_id,
                    "content_topic": chat_.content_topic,
                    "created_at": str(chat_.created_at),
                }

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "data": response,
                        "error": None,
                        "message": "Bot answer generated successfully.",
                    },
                )

        else:
            user_id = current_user.id
            query_text = question
            if not query_text:
                raise HTTPException(status_code=400, detail="Query text is required")

            pine_cone = PineconeExecute(user_id=user_id, texts=query_text)
            query_embedding = pine_cone.embed_text_with_retries(text=query_text)
            if not query_embedding:
                raise HTTPException(
                    status_code=500, detail="Failed to generate query embedding"
                )

            results = pine_cone.search_in_pinecone(query_embedding=query_embedding)

            content = (
                " ".join([res["metadata"]["text"] for res in results])
                if results
                else []
            )

            if content:
                answer = pine_cone.construct_prompt(
                    content=content, question=query_text
                )
            else:
                answer = (
                    "No relevant information found Please provied the valide details."
                )

            chat_ = crud.chat.create(
                db,
                obj_in=schemas.CreateChat(
                    user_id=user_id,
                    question=query_text,
                    answer=answer,
                    session_id=session_id,
                    content_topic=content_topic,
                ),
            )

            response = {
                "id": chat_.id,
                "user_id": chat_.user_id,
                "question": chat_.question,
                "answer": chat_.answer,
                "filename": chat_.filename,
                "url": chat_.url,
                "session_id": chat_.session_id,
                "content_topic": chat_.content_topic,
                "created_at": str(chat_.created_at),
            }

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": response,
                    "error": None,
                    "message": "Bot answer generated successfully.",
                },
            )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )
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




@summary_router.post("/youtube-summary")
async def general_chat(
    url: Optional[str] = Form(None),
    question: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    session_id: Optional[str] = Form(None),
    content_topic: Optional[str] = Form(None),
):
    try:
        if not session_id:
            session_id = str(uuid.uuid4())

        if (question and url):
            raise HTTPException(
                status_code=400,
                detail="Please sent any one 'url' or 'question'.",
            )

        if not question:
            user_id = current_user.id
            analysis = await generate_youtube_summary(
                 url, user_id, background_tasks
            )
            if not analysis:
                raise HTTPException(
                    status_code=400, detail="Error in generating summary"
                )
            if analysis:
                detailed = analysis[0].get("detailed_analysis")

                chat_ = crud.chat.create(
                    db,
                    obj_in=schemas.CreateChat(
                        user_id=current_user.id,
                        answer=detailed,
                        url=url if url else None,
                        session_id=session_id,
                        content_topic=content_topic,
                    ),
                )

                response = {
                    "id": chat_.id,
                    "user_id": chat_.user_id,
                    "question": chat_.question,
                    "answer": chat_.answer,
                    "filename": chat_.filename,
                    "url": chat_.url,
                    "session_id": chat_.session_id,
                    "content_topic": chat_.content_topic,
                    "created_at": str(chat_.created_at),
                }
                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "data": response,
                        "error": None,
                        "message": "Bot answer generated successfully.",
                    },
                )

        else:
            user_id = current_user.id
            query_text = question
            if not query_text:
                raise HTTPException(status_code=400, detail="Query text is required")

            pine_cone = PineconeExecute(user_id=user_id, texts=query_text)
            query_embedding = pine_cone.embed_text_with_retries(text=query_text)
            if not query_embedding:
                raise HTTPException(
                    status_code=500, detail="Failed to generate query embedding"
                )

            results = pine_cone.search_in_pinecone(query_embedding=query_embedding)

            content = (
                " ".join([res["metadata"]["text"] for res in results])
                if results
                else []
            )

            if content:
                answer = pine_cone.construct_prompt(
                    content=content, question=query_text
                )
            else:
                answer = (
                    "No relevant information found Please provied the valide details."
                )

            chat_ = crud.chat.create(
                db,
                obj_in=schemas.CreateChat(
                    user_id=user_id,
                    question=query_text,
                    answer=answer,
                    session_id=session_id,
                    content_topic=content_topic,
                ),
            )

            response = {
                "id": chat_.id,
                "user_id": chat_.user_id,
                "question": chat_.question,
                "answer": chat_.answer,
                "filename": chat_.filename,
                "url": chat_.url,
                "session_id": chat_.session_id,
                "content_topic": chat_.content_topic,
                "created_at": str(chat_.created_at),
            }

            return JSONResponse(
                status_code=200,
                content={
                    "success": True,
                    "data": response,
                    "error": None,
                    "message": "Bot answer generated successfully.",
                },
            )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )
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




@summary_router.delete("/delete-chat/{session_id}")
def clear_chat(
    session_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if not session_id:
        raise HTTPException(status_code=400, detail="session id is required.")

    session_chats = crud.chat.get_chat_history_by_session_id(
        db, current_user.id, session_id
    )

    for session_chat in session_chats:
        crud.chat.remove(db, session_chat.id)

    return JSONResponse(
        status_code=200,
        content={
            "success": True,
            "data": None,
            "error": None,
            "message": "Chat history deleted successfully.",
        },
    )


@summary_router.delete("/delete-all-chat")
def delete_all_chat(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        chat_histories = crud.chat.get_chat_history(db, current_user.id)
        

        for chat_history in chat_histories:
            crud.chat.remove(db, chat_history.id)

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": None,
                "error": None,
                "message": "Deleted all chats.",
            },
        )

    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "success": False,
                "data": None,
                "error": str(e.detail),
                "message": str(e.detail),
            },
        )
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
