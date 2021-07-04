from django.conf import settings
from django.views.decorators.csrf import csrf_protect
from django.core.exceptions import ValidationError
from django.db import models

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, ParseError


from app_auth.utils import has_perm
from master_db.models import MyUser, ClassMetadata, Course
from master_db.serializers import ClassMetadataSerializer
from master_api.utils import get_object_or_404, model_full_clean, edit_object, get_queryset

import datetime

def get_teacher_by_uuid(uuid):
    try:
        teacher = get_object_or_404(MyUser, 'Teacher user', uuid=uuid)
    except ValidationError as message:
        raise ParseError({'detail': list(message)})
    
    verify_teacher(teacher)
    return teacher
    
def get_std_by_uuids(klass, uuids):
    try:
        return get_queryset(klass, uuid__in=uuids)
    except ValidationError as message:
        raise ParseError({'details': list(message)})

def verify_teacher(user):
    # In production
    if not user.mobile == '0919877216':
        raise ParseError('User is not a teacher')


@api_view(['POST'])
@permission_classes([AllowAny])
def create_class(request):
    """
        Take in course_name, name, teacher_uuid (Optional), status (Need revision), std_uuids (Optional)

        Param std_uuids must be in form of: uuid1, uuid2, uuid3 (whitespace is optional)
    """
    std_uuids = request.POST.get('std_uuids')
    teacher = request.POST.get('teacher_uuid')

    # Get course corresponding to course_name
    course = get_object_or_404(
        Course, 'Course', name=request.POST.get('course_name'))

    # Get teacher if available
    if teacher is not None:
        teacher = get_teacher_by_uuid(teacher)

    # Construct model
    now = datetime.datetime.now().timestamp()
    classMeta = ClassMetadata(
        course=course,
        name=request.POST.get('name'),
        teacher=teacher,
        status=request.POST.get('status'),
        created_at=now,
        updated_at=now
    )

    # Validate model
    model_full_clean(classMeta)

    # Get students from std_uuids
    uuids = None
    if std_uuids is not None:
        # Handling UUID validation
        db = get_std_by_uuids(MyUser, std_uuids)

        # Store students id for adding
        students = db.values_list('pk', flat=True)
        # Store uuids for visualizing added students, if one does not show up it is not found
        uuids = db.values_list('uuid', flat=True)

    # Save and add students (M2M field must be added this way to save)
    classMeta.save()
    if std_uuids is not None:
        classMeta.students.add(*students)

    return Response(
        data={
            'teacher_added': not teacher is None,
            'students_added': uuids
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def add_student(request):
    """
        Take in name, uuids. Param name represents class name and uuids is a list of student's uuid

        Param uuids must be in the form of: uuid1, uuid2, uuid3 (whitespace is optional)
    """
    

    # Get class
    classMeta = get_object_or_404(
        ClassMetadata, 'Class', name=request.POST.get('name'))

    # Get all students with uuids
    std_uuids = request.POST.get('uuids')
    uuids = None
    if std_uuids is not None:
        std_uuids = std_uuids.replace(' ', '').split(',')
        # Handling UUID validation
        db = get_std_by_uuids(MyUser, std_uuids)

        # Store students id for adding
        students = db.values_list('pk', flat=True)
        # Store uuids for visualizing added students, if one does not show up it is not found
        uuids = db.values_list('uuid', flat=True)

    # Add students
    classMeta.students.add(*students)

    return Response(
        data={
            'students_added': uuids
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_student(request):
    """
        Take in name and uuids. Param name represents class name, uuids is a list of student uuid.

        Every uuid must be a valid student or else removal will not be performed.

        Param uuids must be in the form of: uuid1, uuid2, uuid3 (whitespace is optional)
    """

    # Get class
    classMeta = get_object_or_404(
        ClassMetadata, 'Class', name=request.POST.get('name'))

    # Get students uuids
    try:
        std_uuids = request.POST.get('uuids').replace(' ', '').split(',')
    except:
        raise ParseError({'uuids': ['This field cannot be null.']})
    # Handling UUID validation
    students = get_std_by_uuids(classMeta.students, std_uuids)
    # Store uuids for visualizing added students, if one does not show up it is not found

    if len(students) != len(std_uuids):
        uuids = (str(o)
                for o in students.values_list('uuid', flat=True).filter())
        raise ParseError(
            {'not_found': list(set(std_uuids).difference(uuids))})

    # Remove students from class if all uuids are present
    classMeta.students.remove(*students)

    return Response(
        data={
            'details': 'Ok',
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def edit_class(request):
    """
        Take in target_name, course_name (optional), teacher_uuid (optional), course (optional), name (optional), status (optional).

        The optional params if not provided will not be updated. If the content provided is the same as the source, no change will be made.

        If at least one optional param is provided, updated_at will be updated
    """
    modifiedDict = request.POST.copy()
    modifiedDict.pop('students', None)
    modifiedDict.pop('created_at', None)
    modifiedDict.pop('updated_at', None)

    # Get class
    classMeta = get_object_or_404(
        ClassMetadata, 'Class', name=request.POST.get('target_name'))

    # Get teacher if provided
    if modifiedDict.get('teacher_uuid') is not None:
        modifiedDict['teacher'] = get_teacher_by_uuid(modifiedDict['teacher_uuid'])

    # Get course if provided
    if modifiedDict.get('course_name') is not None:
        modifiedDict['course'] = get_object_or_404(
            Course, 'Course', name=modifiedDict['course_name'])

    # Update the provided fields if content changed
    modifiedList = []
    edit_object(classMeta, modifiedDict, modifiedList)

    if bool(modifiedList):
        classMeta.updated_at = datetime.datetime.now().timestamp()
        modifiedList.append('updated_at')

    # Validate model
    model_full_clean(classMeta)

    # Save
    classMeta.save()

    return Response(
        data={
            'details': 'Ok',
            'modified': modifiedList,
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_class(request):
    """
        Take in name. Delete exactly one class with the given name.
    """
    # Get class
    classMeta = get_object_or_404(
        ClassMetadata, 'Class', name=request.POST.get('name'))

    # Delete
    classMeta.delete()

    return Response(
        data={
            'details': 'Ok',
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_class(request):
    """
        Take in name (optional), student_uuid (optional). Param student_uuid represents uuid of a student, name represents name of a class. 
        
        If name is provided return explicit info of that class (User info will be provided with name, mobile, email and uuid).

        If student_uuid is provided return all classes of the given student (No explicit info of students, just number of students).
        
        If none is provided return all classes in db with similar format of student_uuid.
        
        Param name has higher priority.
    """
    classMeta = ClassMetadata.objects.all()
    
    # name is provided
    name = request.GET.get('name')
    if name is not None:
        # Get class
        classMeta = get_object_or_404(ClassMetadata, 'Class', name=name)
        return Response(ClassMetadataSerializer(classMeta).data)
    
    # student_uuid is provided
    student_uuid = request.GET.get('uuid')
    if student_uuid is not None:
        # Get student by uuid
        try:
            student = get_object_or_404(MyUser, 'Student', uuid=student_uuid)
        except ValidationError as message:
            raise ParseError({'detail': list(message)})
            
        classMeta = student.student_classes.all()

    data = ClassMetadataSerializer(classMeta, many=True).exclude_field('students').data

    return Response(data)
