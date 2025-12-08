"""
管理端API路由
提供题目管理、导入任务、标签管理、数据导出等功能
"""
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
from pathlib import Path
import uuid
from datetime import datetime
import io

from auth import get_current_user, require_role

router = APIRouter(prefix="/api/admin", tags=["admin"])

DATA_DIR = Path(__file__).parent / "data"
QUESTIONS_FILE = DATA_DIR / "questions.json"
TAGS_FILE = DATA_DIR / "tags.json"
IMPORT_TASKS_FILE = DATA_DIR / "import_tasks.json"
DATA_DIR.mkdir(exist_ok=True)

class QuestionUpdate(BaseModel):
    type: Optional[str] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None
    stemMarkdown: Optional[str] = None
    options: Optional[List[str]] = None
    answer: Optional[str] = None
    solutionMarkdown: Optional[str] = None
    chapterIds: Optional[List[str]] = None
    knowledgePointIds: Optional[List[str]] = None

class BatchUpdateRequest(BaseModel):
    questionIds: List[str]
    updates: QuestionUpdate

class CreateTagRequest(BaseModel):
    name: str
    type: str
    parentId: Optional[str] = None

class UpdateTagRequest(BaseModel):
    name: Optional[str] = None
    parentId: Optional[str] = None

class ExportFilters(BaseModel):
    status: Optional[List[str]] = None
    type: Optional[List[str]] = None
    chapterIds: Optional[List[str]] = None
    knowledgePointIds: Optional[List[str]] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None

@router.get("/questions")
async def get_questions(page: int = Query(1, ge=1), pageSize: int = Query(20, ge=1, le=100),
                       status: Optional[str] = None, type: Optional[str] = None,
                       taskId: Optional[str] = None, keyword: Optional[str] = None,
                       current_user: dict = Depends(get_current_user)):
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        questions = []
    filtered = questions
    if status:
        filtered = [q for q in filtered if q.get('status') == status]
    if type:
        filtered = [q for q in filtered if q.get('type') == type]
    if taskId:
        filtered = [q for q in filtered if q.get('sourceTaskId') == taskId]
    if keyword:
        keyword_lower = keyword.lower()
        filtered = [q for q in filtered if keyword_lower in q.get('stemMarkdown', q.get('question', '')).lower()]
    total = len(filtered)
    start = (page - 1) * pageSize
    end = start + pageSize
    paginated = filtered[start:end]
    return {"questions": paginated, "total": total, "page": page, "pageSize": pageSize}

@router.get("/questions/{question_id}")
async def get_question(question_id: str, current_user: dict = Depends(get_current_user)):
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="题目未找到")
    for q in questions:
        if q.get('questionId') == question_id or q.get('id') == question_id:
            return q
    raise HTTPException(status_code=404, detail="题目未找到")

@router.post("/questions")
async def create_question(question: dict, current_user: dict = Depends(require_role(["admin", "operator"]))):
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        questions = []
    question_id = question.get('id') or question.get('questionId') or f"q_{uuid.uuid4().hex[:8]}"
    question['id'] = question_id
    question['questionId'] = question_id
    question['createdBy'] = current_user['id']
    question['createdAt'] = datetime.now().isoformat()
    question['updatedAt'] = datetime.now().isoformat()
    questions.append(question)
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    return question

@router.put("/questions/{question_id}")
async def update_question(question_id: str, updates: QuestionUpdate,
                        current_user: dict = Depends(get_current_user)):
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="题目未找到")
    for i, q in enumerate(questions):
        if q.get('questionId') == question_id or q.get('id') == question_id:
            update_dict = updates.dict(exclude_unset=True)
            questions[i].update(update_dict)
            questions[i]['updatedAt'] = datetime.now().isoformat()
            with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
            return questions[i]
    raise HTTPException(status_code=404, detail="题目未找到")

@router.delete("/questions/{question_id}")
async def delete_question(question_id: str, current_user: dict = Depends(require_role(["admin"]))):
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="题目未找到")
    original_count = len(questions)
    questions = [q for q in questions if q.get('questionId') != question_id and q.get('id') != question_id]
    if len(questions) == original_count:
        raise HTTPException(status_code=404, detail="题目未找到")
    with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(questions, f, ensure_ascii=False, indent=2)
    return {"message": "删除成功"}

@router.post("/questions/batch-update")
async def batch_update_questions(request: BatchUpdateRequest,
                                current_user: dict = Depends(require_role(["admin", "operator"]))):
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="题目未找到")
    updated_count = 0
    update_dict = request.updates.dict(exclude_unset=True)
    for i, q in enumerate(questions):
        if q.get('questionId') in request.questionIds or q.get('id') in request.questionIds:
            questions[i].update(update_dict)
            questions[i]['updatedAt'] = datetime.now().isoformat()
            updated_count += 1
    if updated_count > 0:
        with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(questions, f, ensure_ascii=False, indent=2)
    return {"updated": updated_count}

@router.get("/import-tasks")
async def get_import_tasks(page: int = Query(1, ge=1), pageSize: int = Query(20, ge=1, le=100),
                          status: Optional[str] = None, startDate: Optional[str] = None,
                          endDate: Optional[str] = None,
                          current_user: dict = Depends(require_role(["admin", "operator"]))):
    try:
        with open(IMPORT_TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f).get('tasks', [])
    except FileNotFoundError:
        tasks = []
    if status:
        tasks = [t for t in tasks if t.get('status') == status]
    total = len(tasks)
    start = (page - 1) * pageSize
    end = start + pageSize
    paginated = tasks[start:end]
    return {"tasks": paginated, "total": total}

@router.post("/import-tasks")
async def create_import_task(file: UploadFile = File(...), sourceType: str = Query(...),
                            name: str = Query(...),
                            current_user: dict = Depends(require_role(["admin", "operator"]))):
    task_id = uuid.uuid4().hex[:8]
    upload_dir = Path(__file__).parent / "data" / "uploads"
    upload_dir.mkdir(exist_ok=True)
    file_path = upload_dir / f"{task_id}_{file.filename}"
    with open(file_path, 'wb') as f:
        content = await file.read()
        f.write(content)
    task = {"id": task_id, "name": name, "sourceFileName": file.filename,
           "sourceFilePath": str(file_path), "sourceType": sourceType,
           "totalQuestions": 0, "status": "pending", "createdBy": current_user['id'],
           "createdAt": datetime.now().isoformat(), "updatedAt": datetime.now().isoformat()}
    try:
        with open(IMPORT_TASKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"tasks": []}
    data["tasks"].append(task)
    with open(IMPORT_TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"taskId": task_id, "status": "pending"}

@router.get("/import-tasks/{task_id}")
async def get_import_task(task_id: str, current_user: dict = Depends(require_role(["admin", "operator"]))):
    try:
        with open(IMPORT_TASKS_FILE, 'r', encoding='utf-8') as f:
            tasks = json.load(f).get('tasks', [])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="任务未找到")
    for task in tasks:
        if task.get('id') == task_id:
            try:
                with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                    questions = json.load(f)
                question_ids = [q.get('id') or q.get('questionId') for q in questions if q.get('sourceTaskId') == task_id]
                task['questions'] = question_ids
            except:
                task['questions'] = []
            return task
    raise HTTPException(status_code=404, detail="任务未找到")

@router.post("/import-tasks/{task_id}/reprocess")
async def reprocess_task(task_id: str, current_user: dict = Depends(require_role(["admin", "operator"]))):
    return {"taskId": task_id, "status": "processing"}

@router.delete("/import-tasks/{task_id}")
async def delete_import_task(task_id: str, deleteQuestions: bool = Query(False),
                            current_user: dict = Depends(require_role(["admin"]))):
    try:
        with open(IMPORT_TASKS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tasks = data.get('tasks', [])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="任务未找到")
    tasks = [t for t in tasks if t.get('id') != task_id]
    data["tasks"] = tasks
    with open(IMPORT_TASKS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    if deleteQuestions:
        try:
            with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
                questions = json.load(f)
            questions = [q for q in questions if q.get('sourceTaskId') != task_id]
            with open(QUESTIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(questions, f, ensure_ascii=False, indent=2)
        except:
            pass
    return {"message": "删除成功"}

@router.get("/tags")
async def get_tags(type: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    try:
        with open(TAGS_FILE, 'r', encoding='utf-8') as f:
            tags = json.load(f).get('tags', [])
    except FileNotFoundError:
        tags = []
    if type:
        tags = [t for t in tags if t.get('type') == type]
    return tags

@router.post("/tags")
async def create_tag(tag: CreateTagRequest, current_user: dict = Depends(require_role(["admin", "teacher"]))):
    try:
        with open(TAGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tags = data.get('tags', [])
    except FileNotFoundError:
        data = {"tags": []}
        tags = []
    new_tag = {"id": uuid.uuid4().hex[:8], "name": tag.name, "type": tag.type,
              "parentId": tag.parentId, "order": len(tags), "usageCount": 0,
              "createdAt": datetime.now().isoformat(), "updatedAt": datetime.now().isoformat()}
    tags.append(new_tag)
    data["tags"] = tags
    with open(TAGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return new_tag

@router.put("/tags/{tag_id}")
async def update_tag(tag_id: str, updates: UpdateTagRequest,
                    current_user: dict = Depends(require_role(["admin", "teacher"]))):
    try:
        with open(TAGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tags = data.get('tags', [])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="标签未找到")
    for i, tag in enumerate(tags):
        if tag.get('id') == tag_id:
            update_dict = updates.dict(exclude_unset=True)
            tags[i].update(update_dict)
            tags[i]['updatedAt'] = datetime.now().isoformat()
            data["tags"] = tags
            with open(TAGS_FILE, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return tags[i]
    raise HTTPException(status_code=404, detail="标签未找到")

@router.delete("/tags/{tag_id}")
async def delete_tag(tag_id: str, current_user: dict = Depends(require_role(["admin"]))):
    try:
        with open(TAGS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            tags = data.get('tags', [])
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="标签未找到")
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        affected = sum(1 for q in questions if tag_id in q.get('chapterIds', []) or tag_id in q.get('knowledgePointIds', []))
    except:
        affected = 0
    tags = [t for t in tags if t.get('id') != tag_id]
    data["tags"] = tags
    with open(TAGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return {"success": True, "affectedQuestions": affected}

@router.post("/export/sft-jsonl")
async def export_sft_jsonl(filters: ExportFilters, current_user: dict = Depends(require_role(["admin"]))):
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        questions = []
    filtered = questions
    if filters.status:
        filtered = [q for q in filtered if q.get('status') in filters.status]
    if filters.type:
        filtered = [q for q in filtered if q.get('type') in filters.type]
    lines = []
    for q in filtered:
        prompt = f"题目：{q.get('stemMarkdown', q.get('question', ''))}\\n"
        if q.get('options'):
            prompt += "选项：\\n"
            for i, opt in enumerate(q.get('options', [])):
                prompt += f"{chr(65+i)}. {opt}\\n"
        completion = f"答案：{q.get('answer', '')}\\n"
        if q.get('solutionMarkdown') or q.get('solution'):
            completion += f"解析：{q.get('solutionMarkdown', q.get('solution', ''))}"
        sft_record = {"prompt": prompt, "completion": completion}
        lines.append(json.dumps(sft_record, ensure_ascii=False))
    content = "\\n".join(lines)
    return StreamingResponse(io.BytesIO(content.encode('utf-8')), media_type="application/jsonl",
                           headers={"Content-Disposition": f"attachment; filename=export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"})

@router.post("/export/questions-json")
async def export_questions_json(filters: ExportFilters, current_user: dict = Depends(require_role(["admin"]))):
    try:
        with open(QUESTIONS_FILE, 'r', encoding='utf-8') as f:
            questions = json.load(f)
    except FileNotFoundError:
        questions = []
    filtered = questions
    if filters.status:
        filtered = [q for q in filtered if q.get('status') in filters.status]
    if filters.type:
        filtered = [q for q in filtered if q.get('type') in filters.type]
    content = json.dumps(filtered, ensure_ascii=False, indent=2)
    return StreamingResponse(io.BytesIO(content.encode('utf-8')), media_type="application/json",
                           headers={"Content-Disposition": f"attachment; filename=export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"})
