from flask import Flask, request, jsonify, abort

app = Flask(__name__)

class Smartphone:
    def __init__(self, number, date_of_add, type_of_tech, model, problem, fio, phone, status):
        self.number = number
        self.date_of_add = date_of_add
        self.type_of_tech = type_of_tech
        self.model = model
        self.problem = problem
        self.fio = fio
        self.phone = phone
        self.status = status

    @classmethod
    def from_dict(cls, data):
        return cls(
            number=data['number'],
            date_of_add=data['date_of_add'],
            type_of_tech=data['type_of_tech'],
            model=data['model'],
            problem=data['problem'],
            fio=data['fio'],
            phone=data['phone'],
            status=data['status']
        )

    def to_dict(self):
        return {
            "number": self.number,
            "date_of_add": self.date_of_add,
            "type_of_tech": self.type_of_tech,
            "model": self.model,
            "problem": self.problem,
            "fio": self.fio,
            "phone": self.phone,
            "status": self.status
        }


smartphones = []
completed_smartphones = []
subscribers = []

@app.route("/smartphones", methods=["POST"])


def create_smartphone():
    data = request.json
    smartphone = Smartphone.from_dict(data)
    smartphones.append(smartphone.to_dict())
    return jsonify(smartphone.to_dict()), 201

@app.route("/smartphones", methods=["GET"])
def read_all_smartphones():
    return jsonify([Smartphone.from_dict(s).to_dict() for s in smartphones]), 200

@app.route("/smartphones/<string:number>", methods=["GET"])
def read_smartphone(number):
    for phone in smartphones:
        if phone["number"] == number:
            return jsonify(Smartphone.from_dict(phone).to_dict()), 200
    abort(404, description="Phone not found")

@app.route("/smartphones/<string:number>", methods=["PUT"])
def update_smartphone(number):
    data = request.json 
    for index, phone in enumerate(smartphones):
        if phone["number"] == number:
            previous_status = smartphones[index]["status"]
            smartphones[index]["status"] = data.get("status", phone["status"])
            if previous_status != "completed" and smartphones[index]["status"] == "completed":
                smartphones[index]["end_time"] = time.time() 
                completed_smartphones.append(smartphones[index])  
                for subscriber in subscribers:
                    if subscriber[1] == number:
                        notify(subscriber[0], number, "Работа завершена")
            return jsonify(smartphones[index]), 200
    abort(404, description="Phone not found")

def notify(address, number, message):
    pass

@app.route("/smartphones/<string:number>/assign_master", methods=["PUT"])
def assign_master(number):
    data = request.json
    for index, phone in enumerate(smartphones):
        if phone["number"] == number:
            smartphones[index]["master"] = data.get("master", phone["master"])
            return jsonify(smartphones[index]), 200
    abort(404, description="Phone not found")

@app.route("/smartphones/<string:number>/comments", methods=["POST"])
def add_comment(number):
    data = request.json
    for index, phone in enumerate(smartphones):
        if phone["number"] == number:
            comment = data.get("comment")
            part = data.get("part")
            if comment:
                smartphones[index]["comments"].append(comment)
            if part:
                smartphones[index]["parts_ordered"].append(part)
            return jsonify(smartphones[index]), 200
    abort(404, description="Phone not found")

@app.route('/smartphones/stats', methods=["GET"])
def get_stats():
    num_completed = len(completed_smartphones)
    total_time = 0
    for phone in completed_smartphones:
        total_time += phone["end_time"] - phone["start_time"]
    mean_time = total_time / num_completed if num_completed > 0 else 0
    problem_stats = {}
    for phone in completed_smartphones:
        problem = phone["problem"]
        if problem in problem_stats:
            problem_stats[problem] += 1
        else:
            problem_stats[problem] = 1
    result = {
        "num_completed": num_completed,
        "mean_time": mean_time,
        "problem_stats": problem_stats
    }
    return jsonify(result)

@app.route('/smartphones/search', methods=["GET"])
def search_smartphones():
    query = request.args.get('query')
    results = []
    for phone in smartphones:
        if query in phone['number'] or query in phone['model'] or query in phone['problem']:
            results.append(Smartphone.from_dict(phone).to_dict())
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
