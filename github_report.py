import requests
import os
import csv
from fpdf import FPDF
from datetime import datetime

# -----------------------
# CONFIGURATION
# -----------------------
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

# -----------------------
# FUNCTIONS
# -----------------------

def get_user_info(username):
    """Fetch GitHub user info"""
    url = f"https://api.github.com/users/{username}"
    return requests.get(url, headers=HEADERS).json()

def get_user_repos(username):
    """Fetch all repositories for a user"""
    url = f"https://api.github.com/users/{username}/repos"
    return requests.get(url, headers=HEADERS).json()

def get_commits(owner, repo):
    """Fetch commit data for a repository"""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    resp = requests.get(url, headers=HEADERS)
    return resp.json() if resp.status_code == 200 else []

def generate_pdf(students_data):
    """Generate a single PDF for multiple students"""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(200, 10, "GitHub Report - Multiple Students", ln=True, align="C")
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)
    pdf.ln(10)

    for regdno, username in students_data:
        pdf.set_font("Arial", "B", 14)
        pdf.cell(200, 10, f"Student: {regdno} ({username})", ln=True)

        user_info = get_user_info(username)
        if "message" in user_info and user_info["message"] == "Not Found":
            pdf.set_font("Arial", size=11)
            pdf.cell(200, 10, f" User {username} not found!", ln=True)
            pdf.ln(5)
            continue

        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, f"Name: {user_info.get('name', 'N/A')}", ln=True)
        pdf.cell(200, 10, f"Public Repos: {user_info.get('public_repos', 0)}", ln=True)
        pdf.ln(5)

        repos = get_user_repos(username)

        pdf.set_font("Arial", "B", 11)
        pdf.cell(70, 8, "Repository", 1)
        pdf.cell(40, 8, "Commits", 1)
        pdf.cell(80, 8, "Last Commit Date", 1, ln=True)

        total_commits = 0
        last_commit_date = None

        pdf.set_font("Arial", size=10)
        for repo in repos[:5]:  # limit to first 5 repos to avoid overload
            repo_name = repo["name"]
            commits = get_commits(username, repo_name)
            count = len(commits)
            last = commits[0]["commit"]["author"]["date"] if count > 0 else "N/A"

            total_commits += count
            if last != "N/A":
                dt = datetime.strptime(last, "%Y-%m-%dT%H:%M:%SZ")
                if last_commit_date is None or dt > last_commit_date:
                    last_commit_date = dt

            pdf.cell(70, 8, repo_name[:25], 1)
            pdf.cell(40, 8, str(count), 1)
            pdf.cell(80, 8, last if last != "N/A" else "-", 1, ln=True)

        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(200, 8, f"Total Repositories: {len(repos)}", ln=True)
        pdf.cell(200, 8, f"Total Commits: {total_commits}", ln=True)
        pdf.cell(200, 8, f"Most Recent Commit: {last_commit_date if last_commit_date else 'N/A'}", ln=True)
        pdf.ln(10)

    filename = "GitHub_MultiStudent_Report.pdf"
    pdf.output(filename)
    print(f" Combined report generated: {filename}")

# -----------------------
# MAIN EXECUTION
# -----------------------
if __name__ == "__main__":
    students = []

    # Read student data from CSV
    with open("students.csv", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            students.append((row["regdno"], row["username"]))

    # You can also limit to first 5–6 students if needed
    students = students[:6]

    generate_pdf(students)
