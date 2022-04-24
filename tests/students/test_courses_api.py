import pytest
from rest_framework.test import APIClient
from students.models import Course, Student
from model_bakery import baker


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs, make_m2m=True)
    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)
    return factory


# проверка получения 1го курса
@pytest.mark.django_db
def test_get_course(client, course_factory, student_factory):
    bob_the_tester = student_factory(name='Bob')
    course_factory(name='Testology', students=[bob_the_tester])
    response = client.get('/courses/1/')
    assert response.status_code == 200


# проверка получения списка курсов
@pytest.mark.django_db
def test_get_course_list(client, course_factory):
    COURSE_SUM = 10
    courses = course_factory(_quantity=COURSE_SUM)
    response = client.get('/courses/')
    assert response.status_code == 200

    data = response.json()
    for i, c in enumerate(data):
        assert c['name'] == courses[i].name


# проверка фильтрации списка курсов по id
@pytest.mark.django_db
def test_get_course_list(client, course_factory):
    COURSE_SUM = 10
    course_factory(_quantity=COURSE_SUM)

    # проверка запроса по id всех курсов
    for i in range(COURSE_SUM):
        response = client.get(f"/courses/?id={i+1}")
        assert response.status_code == 200

    # проверка одного курса с произвольным id
    response = client.get("/courses/?id=5")
    assert response.status_code == 200


# проверка фильтрации списка курсов по name
@pytest.mark.django_db
def test_get_course_list(client, course_factory):
    COURSE_SUM = 10
    courses = course_factory(_quantity=COURSE_SUM)
    response = client.get(f"/courses/?name={courses[9].name}")
    assert response.status_code == 200


# тест успешного создания курса
@pytest.mark.django_db
def test_post_course(client):
    bob_the_tester = Student.objects.create(name='Bob')
    response = client.post('/courses/',
                           data={
                               'name': 'Testology',
                               'students': [bob_the_tester.id]
                           },
                           format='json')
    assert response.status_code == 201


# тест успешного обновления курса
@pytest.mark.django_db
def test_update_course(client, course_factory, student_factory):
    STUDENTS_SUM = 5
    students_group = student_factory(_quantity=STUDENTS_SUM)
    course_factory(name='Testology', students=[students_group[0], students_group[1]])
    response = client.get('/courses/1/')
    assert response.status_code == 200

    response = client.patch('/courses/1/', data={'students': [2, 4]}, format='json')
    assert response.status_code == 200


# тест успешного удаления курса
@pytest.mark.django_db
def test_delete_course(client, course_factory, student_factory):
    bob_the_tester = student_factory(name='Bob')
    course_factory(name='Testology', students=[bob_the_tester])
    response = client.get('/courses/1/')
    assert response.status_code == 200

    response = client.delete('/courses/1/')
    assert response.status_code == 204

    response = client.get('/courses/1/')
    assert response.status_code == 404
