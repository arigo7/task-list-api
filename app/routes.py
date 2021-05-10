from app import db
from flask import Blueprint
from .models.task import Task
from .models.goal import Goal
from flask import request
from flask import jsonify, make_response
from sqlalchemy import asc, desc

# creating instance of the model, first arg is name of app's module
task_bp = Blueprint("tasks", __name__, url_prefix="/tasks")
goal_bp = Blueprint("goals", __name__, url_prefix="/goals")

#create a task with null completed at
@task_bp.route("", methods = ["POST"], strict_slashes = False)
def create_task():
    try:
        request_body = request.get_json()
        new_task = Task(title=request_body["title"],
                description=request_body["description"],
                completed_at = request_body["completed_at"])

        db.session.add(new_task) # "adds model to the db"
        db.session.commit() # commits the action above
        return new_task.to_json_response(), 201
    except KeyError:
        return {"details": "Invalid data"}, 400

#Retrieve all /tasks  asc or desc
@task_bp.route("", methods = ["GET"], strict_slashes = False)
def retrieve_tasks_data():
    tasks = Task.query.all() 
    sort_by = request.args.get("sort") # query parameters 
    tasks_response = []

    if tasks != None: 
        if sort_by != None and sort_by == "asc":  
            # this is a list in asc order, .all() comes at the end
            tasks_asc = Task.query.order_by(Task.title.asc()).all() 
            # this puts it in the right order for the response body:
            tasks_response_asc = [task_asc.task_to_json_response() \
                for task_asc in tasks_asc]
            return jsonify(tasks_response_asc), 200
        
        elif sort_by != None and sort_by == "desc":
            # this is a list in desc order
            tasks_asc = Task.query.order_by(Task.title.desc()).all() 
            # this puts it in the right order for the response body:
            tasks_response_desc = [task_asc.task_to_json_response() \
                for task_asc in tasks_asc]
            return jsonify(tasks_response_desc), 200

        for task in tasks:
            tasks_response.append(task.task_to_json_response())
        return jsonify(tasks_response), 200  # list of all tasks
    return jsonify(tasks_response), 200 ## OR #return tasks_response, 200

# Retrieve one /task/1     
@task_bp.route("/<task_id>", methods=["GET"])
def retrieve_single_task(task_id):
    task = Task.query.get(task_id)
    if task != None:
        # return task.to_json_response(), 200
        response = task.to_json_response()
        if task.goal_id:
            response['task']['goal_id'] = task.goal_id
        return response, 200
    return make_response('', 404)

#Update a task
@task_bp.route("/<task_id>", methods=["PUT"])  
def update_task(task_id):
    task = Task.query.get(task_id)
    if task: # if successful quering task with given task_id
        # save user input form_data as json format
        form_data = request.get_json()  
        # updating instance of model with task_id, first the title 
        task.title = form_data["title"]  
        # updating model description field for task = task_id
        task.description = form_data["description"] 
        # and completed at
        task.completed_at = form_data["completed_at"] 
        db.session.commit() # commiting changes to db
        return task.to_json_response(), 200
    return make_response(""), 404

# Delete a task
@task_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):  
    task = Task.query.get(task_id) 
    if task != None:
        db.session.delete(task)
        db.session.commit()
        details_str = f"Task {task_id} \"{task.title}\" successfully deleted"
        return jsonify(details = details_str), 200
    return make_response(""), 404

# Modify part of a task to mark complete
@task_bp.route("/<task_id>/mark_complete", methods=["PATCH"])  
def patch_task_mark_complete(task_id):
    task = Task.query.get(task_id) ## getting the task by id (its whole body)
    # PATCHing if: arg mark_complete specified # in URL and task id 
    # provided exists in database
    if task:                         
        # then call function that changes it to complete
        task.set_completion() # updates it with a date in "completed_at" field
        # print(task.set_completion())
        db.session.commit()
        return task.to_json_response(), 200
    return make_response(""), 404

# Modify part of a task to mark incomplete
@task_bp.route("/<task_id>/mark_incomplete", methods=["PATCH"])  
def patch_task_mark_incomplete(task_id):
    task = Task.query.get(task_id)
    if task:
        task.completed_at = None
        db.session.commit()
        return task.to_json_response(), 200
    return make_response(""), 404

# GOAL ROUTES start here 
@goal_bp.route("", methods = ["POST"], strict_slashes = False)
def create_goal():
    try:
        request_body = request.get_json()
        new_goal = Goal(title=request_body["title"])
        db.session.add(new_goal) # "adds model to the db"
        db.session.commit() # does the action above
        return new_goal.goal_to_json_response(), 201
    except KeyError:
        return {"details": "Invalid data"}, 400

#Retrieve all /goals 
@goal_bp.route("", methods = ["GET"], strict_slashes = False)
def retrieve_goals_data():
    goals = Goal.query.all() 
    goals_response = []

    if goals != None:
        for goal in goals:
            goals_response.append(goal.simple_response())
        return jsonify(goals_response), 200  # returning list of all goals
    return jsonify(goals_response), 200 ## OR #return goals_response, 200 

# Retrieve one /goal/1     
@goal_bp.route("/<goal_id>", methods=["GET"])
def retrieve_single_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal != None:
        return goal.goal_to_json_response(), 200
    return make_response('', 404)

# Delete a goal
@goal_bp.route("/<goal_id>", methods=["DELETE"])
def delete_goal(goal_id):  
    goal = Goal.query.get(goal_id) 
    if goal != None:
        db.session.delete(goal)
        db.session.commit()
        details_str = f"Goal {goal_id} \"{goal.title}\" successfully deleted"
        return jsonify(details = details_str), 200    
    return make_response(""), 404

# Update a goal
@goal_bp.route("/<goal_id>", methods=["PUT"])  
def update_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if goal: # successful updating goal
        form_data = request.get_json() # save user input form_data as json format 
        goal.title = form_data["title"] # updating model
        db.session.commit()
        return goal.goal_to_json_response(), 200
    return make_response(""), 404  #NOT FOUND ERROR VS 400 - BAD REQ


# ONE TO MANY RELATIONSHIP - /goals/<goal_id>/tasks - routes
@goal_bp.route("/<goal_id>/tasks", methods = ["POST"])
def post_task_ids_to_goal(goal_id):
    try: 
        request_body = request.get_json()  
        goal = Goal.query.get(goal_id)  # instance of this goal_id including 
                                        # the task ids
        # store list of tasks given in the request body (task_ids)
        task_ids = request_body["task_ids"]  # task_ids - list ie. [1,3,4]
        for task_id in task_ids:
            task = Task.query.get(task_id)  
            # appending those tasks queried into goal with given id
            goal.tasks.append(task) # this is a field 
            db.session.commit()
        # display this info into response as json and integers not strings
        return {"id": int(goal_id), "task_ids": task_ids},200
    except:
        return make_response(""), 404 ## not found

@goal_bp.route("/<goal_id>/tasks", methods = ["GET"])
def getting_tasks_of_one_goal(goal_id):
    goal = Goal.query.get(goal_id) 
    if goal: 
        tasks = goal.tasks
        # create a list of tasks and each task CALL FUNCTION task.task_to_json_response()
        new_list = [task.task_to_json_response_w_goal() for task in tasks]
        return {"id": goal.goal_id,
            "title": goal.title,
            "tasks": new_list}, 200
    # if goal doesn't exist
    return make_response(""), 404
        

        