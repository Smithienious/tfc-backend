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
from master_api.utils import get_object_or_404, model_full_clean

import datetime


def verify_teacher(user):
    # In production
    return user.mobile == '0919877216'


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
        teacher = get_object_or_404(MyUser, 'Teacher user', uuid=teacher)

        if not verify_teacher(teacher):
            return Response(
                data={
                    'details': 'Error',
                    'message': 'User is not a teacher'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

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
    if not std_uuids is None:
        # Handling UUID validation
        try:
            db = MyUser.objects.filter(
                uuid__in=std_uuids.replace(' ', '').split(','))
        except ValidationError as message:
            raise ParseError(message)

        # Store students id for adding
        students = db.values_list('pk', flat=True)
        # Store uuids for visualizing added students, if one does not show up it is not found
        uuids = db.values_list('uuid', flat=True)

    # Save and add students (M2M field must be added this way to save)
    classMeta.save()
    if not std_uuids is None:
        classMeta.students.add(*students)

    return Response(
        data={
            'details': 'Ok',
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
    std_uuids = request.POST.get('uuids')

    # Get class
    classMeta = get_object_or_404(
        ClassMetadata, 'Class', name=request.POST.get('name'))

    # Get all students with uuids
    uuids = None
    if not std_uuids is None:
        std_uuids = std_uuids.replace(' ', '').split(',')
        # Handling UUID validation
        try:
            db = MyUser.objects.filter(uuid__in=std_uuids)
        except ValidationError as message:
            raise ParseError(detail=message)

        # Store students id for adding
        students = db.values_list('pk', flat=True)
        # Store uuids for visualizing added students, if one does not show up it is not found
        uuids = db.values_list('uuid', flat=True)

    # Add students
    classMeta.students.add(*students)

    return Response(
        data={
            'details': 'Ok',
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
    std_uuids = request.POST.get('uuids')

    # Get class
    classMeta = get_object_or_404(
        ClassMetadata, 'Class', name=request.POST.get('name'))

    # Get students uuids
    uuids = None
    if not std_uuids is None:
        std_uuids = std_uuids.replace(' ', '').split(',')
        # Handling UUID validation
        try:
            students = classMeta.students.filter(uuid__in=std_uuids)
        except ValidationError as message:
            raise ParseError(message)
        # Store uuids for visualizing added students, if one does not show up it is not found
        uuids = [str(o)
                 for o in students.values_list('uuid', flat=True).filter()]

        if len(uuids) != len(std_uuids):
            raise ParseError(
                {'not_found': list(set(std_uuids).difference(set(uuids)))})

    # Remove students from class if all uuids are present
    classMeta.students.remove(*students.values_list('pk', flat=True))

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
        Take in target_name, course_name (optional), teacher (optional), course (optional), name (optional), status (optional).

        The optional params if not provided will not be updated. If the content provided is the same as the source, no change will be made.

        If at least one optional param is provided, updated_at will be updated
    """
    modifiedDict = request.POST.copy()
    modifiedDict.pop('students')
    modifiedDict.pop('created_at')
    modifiedDict.pop('updated_at')

    # Get class
    classMeta = get_object_or_404(
        ClassMetadata, 'Class', name=request.POST.get('target_name'))

    # Get teacher if provided
    if not modifiedDict.get('teacher') is None:
        modifiedDict['teacher'] = get_object_or_404(
            MyUser, 'Teacher user', uuid=modifiedDict['teacher'])

        if not verify_teacher(modifiedDict['teacher']):
            raise ParseError('User is not a teacher')

    # Get course if provided
    if not modifiedDict.get('course') is None:
        modifiedDict['course'] = get_object_or_404(
            Course, 'Course', name=modifiedDict['course'])

    # Update the provided fields if content changed
    modifiedList = []
    for key, value in modifiedDict.items():
        if hasattr(classMeta, key) and value != getattr(classMeta, key):
            setattr(classMeta, key, value)
            modifiedList.append(key)

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
            # ! For testing purposes only, should be removed
            'data': ClassMetadataSerializer(classMeta).data
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
            # ! For testing purposes only, should be removed
            'data': ClassMetadataSerializer(classMeta).data,
        },
        status=status.HTTP_202_ACCEPTED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_class(request):
    """
        Take in uuid (optional). This represents uuid of a student. 

        If uuid is provided return all classes of the given student, else return all classes in db with number of students in each class.
    """
    uuid = request.GET.get('uuid')
    if uuid is None:
        classMeta = ClassMetadata.objects
    else:
        # Get student by uuid
        try:
            student = MyUser.objects.get(uuid=uuid)
        except (MyUser.DoesNotExist, ValidationError) as e:
            if type(e).__name__ == 'DoesNotExist':
                message = 'Student does not exist'
                stat = status.HTTP_404_NOT_FOUND
            else:
                message = e
                stat = status.HTTP_400_BAD_REQUEST
            return Response(
                data={
                    'detail': message
                },
                status=stat
            )
        classMeta = student.students_classes

    classMeta = classMeta.annotate(teacher_name=models.functions.Concat('teacher__last_name', models.Value(
        ' '), 'teacher__mid_name', models.Value(' '), 'teacher__first_name', output_field=models.TextField()))
    view = ['name', 'course__name', 'teacher_name', 'teacher__uuid', 'status']
    if uuid is None:
        classMeta = classMeta.annotate(num_students=models.Count(
            'students')).order_by('-num_students')
        view.append('num_students')

    return Response(
        data=classMeta.all().values(*view)
    )
