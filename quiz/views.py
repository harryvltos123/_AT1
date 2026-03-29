import random
from django.shortcuts import render, redirect
from .data import COUNTRIES, QUESTION_COUNTS


def difficulty(request):
    # difficulty selection
    if request.method == "POST":
        level = request.POST.get("difficulty")
        if level not in COUNTRIES:
            return redirect("quiz:difficulty")

        # build and shuffle question list, store in session
        questions = COUNTRIES[level].copy()
        random.shuffle(questions)
        count = QUESTION_COUNTS[level]
        questions = questions[:count]

        request.session["difficulty"] = level
        request.session["questions"] = questions
        request.session["current"] = 0
        request.session["score"] = 0
        request.session["total"] = count

        return redirect("quiz:question")

    return render(request, "quiz/difficulty.html")


def question(request):
    # show the current question and handle answer submission
    questions = request.session.get("questions")
    current = request.session.get("current", 0)
    total = request.session.get("total", 0)

    if not questions or current >= total:
        return redirect("quiz:results")

    q = questions[current]
    feedback = None
    hint = request.session.pop("hint", None)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "hint":
            request.session["hint"] = q["hint"]
            return redirect("quiz:question")

        answer = request.POST.get("answer", "").strip()
        correct = q["capital"]

        if answer.lower() == correct.lower():
            request.session["score"] += 1
            request.session["current"] += 1
            request.session.modified = True

            if request.session["current"] >= total:
                return redirect("quiz:results")
            return redirect("quiz:question")
        else:
            feedback = "incorrect"

    return render(request, "quiz/question.html", {
        "country": q["name"],
        "flag_code": q["code"],
        "question_num": current + 1,
        "total": total,
        "difficulty": request.session.get("difficulty"),
        "feedback": feedback,
        "hint": hint,
    })


def results(request):
    # show final score.
    score = request.session.get("score", 0)
    total = request.session.get("total", 0)
    difficulty = request.session.get("difficulty", "")

    # clear quiz session data
    for key in ["questions", "current", "score", "total"]:
        request.session.pop(key, None)

    return render(request, "quiz/results.html", {
        "score": score,
        "total": total,
        "difficulty": difficulty,
    })

