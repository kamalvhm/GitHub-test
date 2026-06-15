from copy import deepcopy

from fastapi.testclient import TestClient

from src.app import app, activities


def setup_module(module):
    module._original_activities = deepcopy(activities)


def teardown_module(module):
    activities.clear()
    activities.update(module._original_activities)


def test_get_activities_returns_activity_list():
    # Arrange
    client = TestClient(app)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    response_data = response.json()
    assert "Chess Club" in response_data
    assert response_data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_for_activity_adds_student():
    # Arrange
    client = TestClient(app)
    activity_name = "Art Club"
    student_email = "newstudent@mergington.edu"
    assert student_email not in activities[activity_name]["participants"]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": student_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {student_email} for {activity_name}"}
    assert student_email in activities[activity_name]["participants"]


def test_signup_for_activity_returns_404_when_activity_missing():
    # Arrange
    client = TestClient(app)
    missing_activity = "Nonexistent Club"

    # Act
    response = client.post(f"/activities/{missing_activity}/signup", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_for_activity_returns_400_for_duplicate_email():
    # Arrange
    client = TestClient(app)
    activity_name = "Chess Club"
    duplicate_email = activities[activity_name]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": duplicate_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_unregister_from_activity_removes_student():
    # Arrange
    client = TestClient(app)
    activity_name = "Programming Class"
    student_email = "to_remove@mergington.edu"
    if student_email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(student_email)

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": student_email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {student_email} from {activity_name}"}
    assert student_email not in activities[activity_name]["participants"]


def test_unregister_from_activity_returns_404_when_activity_missing():
    # Arrange
    client = TestClient(app)
    missing_activity = "Nonexistent Club"

    # Act
    response = client.delete(f"/activities/{missing_activity}/unregister", params={"email": "student@mergington.edu"})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_returns_400_when_student_not_enrolled():
    # Arrange
    client = TestClient(app)
    activity_name = "Gym Class"
    missing_email = "not_enrolled@mergington.edu"
    assert missing_email not in activities[activity_name]["participants"]

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": missing_email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
