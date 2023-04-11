# Course Schedule Optimizer

![course_graph](https://user-images.githubusercontent.com/2356749/231145396-bff860b0-5b35-4ac2-b347-9561dbaf69f5.png)

**This project is not yet optimized**

This is a course schedule optimizer that helps students to create a personalized schedule based on their preferences. The program reads course data from JSON files and generates an optimized timetable, considering constraints such as class timings, credit limits, and preferred days.


# Features
- Parses course data from JSON files
- Creates a conflict graph of courses based on class timings
- Optimizes the course schedule based on student preferences
- Maximum number of courses
- Maximum number of credits
- Preferred days
- Preferred credits
- Preferred subjects
- Preferred language
- Generates a timetable image of the optimized schedule


# Getting Started

## Dependencies

Python 3.6 or higher,
glob,
itertools,
re,
matplotlib,
networkx,
pandas,
ujson

## Usage

Clone the repository.

Ensure that the course data JSON files are in the data/ folder.

Run main.py to start the optimization process.

The program generates a course_graph.png file with the conflict graph of courses and a timetable.png file with the optimized timetable.

You can look up [here](https://github.com/Alfex4936/Ajou-Parser/tree/main) to parse classes.

## Example Course Data Format

The course data JSON files should have the following structure:

```json
{
  "subject_code": "SCE492",
  "abee_point": 1,
  "class_time": "Mon D(Pal 108) Thu D(Pal 108)",
  "classroom": "팔108",
  "course_category": "전선",
  "course_type": "Required Course",
  "credit_points": 3,
  "department_english": "Software and Computer Engineering",
  "department_name": "소프트웨어학과",
  "main_lecturer_employee_number": "201610002",
  "main_lecturer_english_name": "Hwanyong Lee",
  "main_lecturer_name": "이환용",
  "subject_english_name": "SW Business Start-up",
  "subject_id": "20140224",
  "subject_korean_name": "SW창업론",
  "year": "2023"
}
```

# Example Output

The data was tested with 2023-1 courses. (Total 1772)

```py
# Settings
optimized_schedule = optimize_schedule(
    course_graph,
    max_courses=6,
    max_credits=21,
    preferred_days={2, 3, 4, 5},  # Tue, Wed, Thur, Fri
    preferred_credits={3},  # Only 3-credit courses
    preferred_subjects={"아주강좌1"},  # Only courses with these subjects
    # preferred_language="English",  # Only English courses
)

# Output
Subject ID: 12011, Korean Name: 아주강좌1, English Name: Ajou Lecture 1, Credit: 1

Subject ID: 20110485, Korean Name: 마음챙김과 자기조절, English Name: Mindfulness & self-regulation, Credit: 3

Subject ID: 20190337, Korean Name: 생물다양성과 진화, English Name: Biodiversity and Evolution, Credit: 3

Subject ID: 10371, Korean Name: 구조역학, English Name: Theory of Structure in Architecture, Credit: 3

Subject ID: 20140544, Korean Name: 범죄와 현대사회, English Name: Crimes in Modern Society, Credit: 3

Subject ID: 20220315, Korean Name: 의학연구입문, English Name: Introduction to Medical Research, Credit: 3
```



# License

This project is licensed under the MIT License.