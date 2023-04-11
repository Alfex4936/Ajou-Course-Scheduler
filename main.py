import glob
import itertools
import re

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import ujson

# Set the font family that supports Korean characters
plt.rcParams["font.family"] = "HYGothic-Medium"


class TimeSlot:
    def __init__(self, day, time):
        self.day = day
        self.time = time

    def __eq__(self, other):
        if isinstance(other, TimeSlot):
            return self.day == other.day and self.time == other.time
        return False

    def __hash__(self):
        return hash((self.day, self.time))

    def conflicts_with(self, other):
        if self.day != other.day:
            return False
        time_self = float(self.time[:-3])
        time_other = float(other.time[:-3])
        return abs(time_self - time_other) < 1


def read_json_file(file_name):
    with open(file_name, "r", encoding="utf-8") as file:
        return ujson.load(file)


file_pattern = "data/*.json"
file_names = glob.glob(file_pattern)
data = []

for file_name in file_names:
    file_data = read_json_file(file_name)
    data.extend(file_data)


# Convert the data to a DataFrame
df_courses = pd.DataFrame(data)


def keep_unique_times(group):
    group = group.drop_duplicates(subset=["class_time"])
    return group


# Group by 'subject_korean_name' and apply the custom function
df_courses = (
    df_courses.groupby("subject_korean_name", as_index=False)
    .apply(keep_unique_times)
    .reset_index(drop=True)
)


print(len(df_courses))


def save_graph_as_png(G, file_name):
    plt.figure(figsize=(30, 30))
    pos = nx.spring_layout(G, seed=42)  # type: ignore
    nx.draw(G, pos, node_size=500, node_color="lightblue", with_labels=True)  # type: ignore
    nx.draw_networkx_edge_labels(G, pos)  # type: ignore
    plt.savefig(file_name)
    plt.close()


def create_course_graph(courses_df):
    G = nx.Graph()

    for index, course in courses_df.iterrows():
        G.add_node(course["subject_id"], **course.to_dict())

    for course1, course2 in itertools.combinations(courses_df["subject_id"], 2):
        if has_time_conflict(
            G.nodes[course1]["class_time_processed"],
            G.nodes[course2]["class_time_processed"],
        ):
            G.add_edge(course1, course2)

    return G


def preprocess_class_time(class_time):
    class_time = class_time.strip()
    time_slots = []

    # Check if the class_time is empty and return an empty list if it is
    if not class_time:
        return []

    day_to_code = {
        "Mon": 1,
        "Tue": 2,
        "Wed": 3,
        "Thu": 4,
        "Fri": 5,
        "Sat": 6,
        "Sun": 7,
    }

    pattern = r"(\w{3})\s+(\d(?:\.\d)?)(?:\([^)]*\))"
    matches = re.findall(pattern, class_time)

    for day, time in matches:
        day_code = day_to_code.get(day[:3], None)
        if day_code is not None:
            time_value = float(time)
            time_code = chr(int(time_value * 2) + ord("A") - 2)
            time_slots.append(TimeSlot(day_code, time_code))

    return time_slots


def has_time_conflict(time_slots1, time_slots2):
    for ts1 in time_slots1:
        for ts2 in time_slots2:
            if ts1.day == ts2.day and ts1.time == ts2.time:
                return True
    return False


def optimize_schedule(
    course_graph,
    max_courses=None,
    max_credits=21,
    preferred_days=None,
    preferred_credits=None,
    preferred_subjects=None,
    preferred_language=None,
):
    def is_better_course(course1, course2):
        conflicts1 = len(
            [nbr for nbr in course_graph[course1] if nbr in available_courses]
        )
        conflicts2 = len(
            [nbr for nbr in course_graph[course2] if nbr in available_courses]
        )

        if conflicts1 < conflicts2:
            return True

        if conflicts1 == conflicts2:
            credits1 = course_graph.nodes[course1]["credit_points"]
            credits2 = course_graph.nodes[course2]["credit_points"]

            if credits1 == 3 and credits2 != 3:
                return True
            if credits1 != 3 and credits2 == 3:
                return False
            if credits1 > credits2:
                return True

        return False

    def filter_courses_by_preferences(course):
        course_info = course_graph.nodes[course]

        if (
            preferred_subjects
            and course_info["subject_korean_name"] in preferred_subjects
        ):
            return True

        if preferred_days:
            class_times = course_info["class_time_processed"]
            if not any(slot.day in preferred_days for slot in class_times):
                return False

        if preferred_credits and course_info["credit_points"] not in preferred_credits:
            return False

        if preferred_language and course_info["course_language"] != preferred_language:
            return False

        return True

    selected_courses = []

    available_courses = {
        course
        for course in course_graph.nodes
        if (
            (
                "1학년" in course_graph.nodes[course]["recommended_year"]
                or "2학년" in course_graph.nodes[course]["recommended_year"]
                or "3학년" in course_graph.nodes[course]["recommended_year"]
                or "4학년" in course_graph.nodes[course]["recommended_year"]
                or course_graph.nodes[course]["recommended_year"] == ""
            )
            and (
                filter_courses_by_preferences(course)
                or (
                    preferred_subjects
                    and course_graph.nodes[course]["subject_korean_name"]
                    in preferred_subjects
                )
            )
        )
    }

    # Add preferred_subjects first
    if preferred_subjects:
        for course in course_graph.nodes:
            course_info = course_graph.nodes[course]
            if course_info["subject_korean_name"] in preferred_subjects:
                selected_courses.append(course)
                if course in available_courses:
                    available_courses.remove(course)
                available_courses -= set(course_graph[course])

    # Continue with the rest of the optimization
    while available_courses:
        best_course = None

        for course in available_courses:
            if best_course is None or is_better_course(course, best_course):
                best_course = course

        # Print the course information
        course_info = course_graph.nodes[best_course]

        selected_courses.append(best_course)
        available_courses.remove(best_course)
        available_courses -= set(course_graph[best_course])

        if max_courses and len(selected_courses) >= max_courses:
            break
        if (
            max_credits
            and sum(
                course_graph.nodes[course]["credit_points"]
                for course in selected_courses
            )
            >= max_credits
        ):
            break

    # Print all selected courses
    print("\nSelected courses:")
    for course in selected_courses:
        course_info = course_graph.nodes[course]
        print(
            f"Subject ID: {course_info['subject_id']}, "
            f"Korean Name: {course_info['subject_korean_name']}, "
            f"English Name: {course_info['subject_english_name']}, "
            f"Credit: {course_info['credit_points']}"
        )

    return selected_courses


def plot_timetable(schedule, course_graph, file_name):
    print("Generating timetable...")
    days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    time_labels = [
        "9:00 AM",
        "9:30 AM",
        "10:00 AM",
        "10:30 AM",
        "11:00 AM",
        "11:30 AM",
        "12:00 PM",
        "12:30 PM",
        "1:00 PM",
        "1:30 PM",
        "2:00 PM",
        "2:30 PM",
        "3:00 PM",
        "3:30 PM",
        "4:00 PM",
        "4:30 PM",
        "5:00 PM",
        "5:30 PM",
        "6:00 PM",
        "6:30 PM",
        "7:00 PM",
        "7:30 PM",
    ]

    footer = []
    timetable = [[[] for _ in range(len(time_labels))] for _ in range(len(days))]

    for course in schedule:
        course_info = course_graph.nodes[course]
        korean_name = course_info["subject_korean_name"]
        classroom = course_info["classroom"]
        professor = course_info["main_lecturer_name"]
        class_time = course_info["class_time_processed"]

        if not class_time:
            footer.append(f"{korean_name} ({classroom}, {professor})")
            continue

        for time_slot in class_time:
            day_code = time_slot.day - 1
            time_code = ord(time_slot.time) - ord("A")
            timetable[day_code][time_code].append(
                f"{korean_name}\n({classroom}, {professor})"
            )

    _, ax = plt.subplots(figsize=(14, 8))

    print(len(time_labels))

    ax.axis("off")
    table = ax.table(
        cellText=timetable,
        colLabels=days,
        rowLabels=time_labels,
        cellLoc="center",
        loc="center",
    )

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.6, 2.2)  # square size

    if footer:
        footer_text = "Courses without class time: " + ", ".join(footer)
        plt.figtext(
            0.5, 0.01, footer_text, wrap=True, horizontalalignment="center", fontsize=12
        )

    plt.savefig(file_name, bbox_inches="tight")
    plt.close()


df_courses["class_time_processed"] = df_courses["class_time"].apply(
    preprocess_class_time
)
course_graph = create_course_graph(df_courses)
optimized_schedule = optimize_schedule(
    course_graph,
    max_courses=6,
    preferred_days={2, 3, 4, 5},  # Monday, Wednesday, Friday
    preferred_credits={3},  # Only 3-credit courses
    preferred_subjects={"아주강좌1"},  # Only courses with these subjects
    # preferred_language="English",  # Only English courses
)

save_graph_as_png(course_graph, "course_graph.png")

# lot_timetable(optimized_schedule, course_graph, "timetable.png")
