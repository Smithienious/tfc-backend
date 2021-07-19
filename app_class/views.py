from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from master_api.utils import get_by_uuid
from master_api.views import get_object, create_object, delete_object, edit_object
from master_db.models import CustomUser, ClassMetadata, Course
from master_db.serializers import ClassMetadataSerializer

import datetime


CustomUser = get_user_model()


def get_std_by_uuids(klass, uuids):
    try:
        return klass.objects.filter(uuid__in=uuids)
    except ValidationError as message:
        raise ParseError({'details': list(message)})


@api_view(['POST'])
@permission_classes([AllowAny])
def create_class(request):
    return create_object(ClassMetadata, data=request.data)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def edit_class(request):
    return edit_object(ClassMetadata, data=request.data)


@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_protect
def delete_class(request):
    return delete_object(ClassMetadata, data=request.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_class(request):
    return get_object(ClassMetadata, data=request.GET)


@api_view(['POST'])
@permission_classes([AllowAny])
def add_student(request):
    """
        Take in uuid, student_uuids. Param uuid represents class 
        with the given uuid, student_uuids is a list of student's 
        uuid

        Param student_uuids must be in the form of: uuid1, uuid2, 
        uuid3 (whitespace is optional)
    """
    CustomUser = get_user_model()

    # Get class
    classMeta = get_by_uuid(
        ClassMetadata, request.POST.get('uuid'))

    # Get all students with uuids
    std_uuids = request.POST.get('student_uuids')
    if std_uuids is None:
        raise ParseError({'student_uuids': ['This field is required.']})

    std_uuids = std_uuids.replace(' ', '').split(',')
    # Handling UUID validation
    db = get_std_by_uuids(CustomUser, std_uuids)

    # Store students id for adding
    students = db.values_list('pk', flat=True)
    # Store uuids for visualizing added students, if one does not show up it is not found
    uuids = db.values_list('uuid', flat=True)

    # Add students
    classMeta.students.add(*students)
    if bool(uuids):
        classMeta.save()

    return Response({'students_added': uuids})


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_student(request):
    """
        Take in uuid and student_uuids. Param uuid represents class 
        with the given uuid, student_uuids is a list of student uuid.

        Every uuid in student_uuids must be a valid student or else 
        removal will not be performed.

        Param student_uuids must be in the form of: uuid1, uuid2, 
        uuid3 (whitespace is optional)
    """

    # Get class
    classMeta = get_by_uuid(
        ClassMetadata, request.POST.get('uuid'))

    # Get students uuids
    try:
        std_uuids = request.POST.get(
            'student_uuids').replace(' ', '').split(',')
    except:
        raise ParseError({'student_uuids': ['This field is required.']})

    # Get students
    students = get_std_by_uuids(classMeta.students, std_uuids)

    # Store uuids for visualizing added students, if one does not show up it is not found
    if len(students) != len(std_uuids):
        uuids = (str(o)
                 for o in students.values_list('uuid', flat=True).filter())
        raise ParseError(
            {'not_found': list(set(std_uuids).difference(uuids))})

    # Remove students from class if all uuids are present
    classMeta.students.remove(*students)
    classMeta.save()

    return Response({'details': 'Ok'})


@api_view(['GET'])
@permission_classes([AllowAny])
def list_class(request):
    """
        Take in student_uuid (optional). Param student_uuid represents 
        uuid of a student. 

        If student_uuid is provided return all classes of the given 
        student (No explicit info of students, just number of students).

        If none is provided return all classes in db with similar 
        format of student_uuid.
    """
    classMeta = ClassMetadata.objects.all()

    # student_uuid is provided
    student_uuid = request.GET.get('student_uuid')
    if student_uuid is not None:
        # Get student by uuid
        student = get_by_uuid(CustomUser, student_uuid)

        classMeta = student.student_classes.all()

    data = ClassMetadataSerializer(
        classMeta, many=True).data

    return Response(data)
