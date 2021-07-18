from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect

from rest_framework import status
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from master_api.utils import get_object_or_404, model_full_clean, edit_object, get_by_uuid
from master_db.models import ClassMetadata, Schedule
from master_db.serializers import ScheduleSerializer

import datetime


CustomUser = get_user_model()

def validate_sched(sched):
    model_full_clean(sched)

    # Validate time
    if sched.time_end <= sched.time_start:
        raise ParseError('Time end must be greater than time start')

    return None


@api_view(['POST'])
@permission_classes([AllowAny])
def create_sched(request):
    """
        Take in class_name, time_start, time_end, time_end must be greater than time_start and both are int
    """
    # Get class
    classroom = get_object_or_404(
        ClassMetadata, 'Class', name=request.POST.get('class_name'))

    # Get model
    time_start = request.POST.get('time_start')
    time_end = request.POST.get('time_end')
    now = datetime.datetime.now().timestamp()
    sched = Schedule(
        classroom=classroom,
        time_start=time_start,
        time_end=time_end,
        created_at=now,
        updated_at=now
    )

    # Validate model
    validate_sched(sched)

    # Save
    sched.save()

    return Response(
        data={'detail': 'Ok'},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def edit_sched(request):
    """
        Take in uuid, classroom (optional), time_start (optional), time_end (optional). time_start and time_end must be integers.

        The optional params if not provided will not be updated. If the content provided is the same as the source, no change will be made.

        If at least one optional param is provided, updated_at will be updated.
    """
    # Get params and convert some to int
    modifiedDict = request.POST.copy()

    # Get schedule
    sched = get_by_uuid(Schedule, 'Schedule',
                              modifiedDict.get('uuid'))

    # Get classroom if necessary
    if not modifiedDict.get('classroom') is None:
        modifiedDict['classroom'] = get_object_or_404(
            ClassMetadata, 'Class', name=modifiedDict['classroom'])

    # Make changes
    modifiedList = edit_object(sched, modifiedDict)

    # If changed update modified
    if not modifiedList:
        return Response(data={'detail': 'modified nothing'}, status=status.HTTP_304_NOT_MODIFIED)
    else:
        modifiedList.append('modified')

    # Validate model
    validate_sched(sched)

    # Save
    sched.save()

    return Response({'modified': modifiedList})


@api_view(['POST'])
@permission_classes([AllowAny])
def delete_sched(request):
    """
        Take in uuid and delete sched with the following uuid.
    """
    get_by_uuid(Schedule, 'Schedule', request.POST.get('uuid')).delete()

    return Response({'detail': 'Deleted'})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_sched(request):
    """
        Take in uuid. 

        Return explicit info of that schedule.
    """
    return Response(
        ScheduleSerializer(
            get_by_uuid(Schedule, 'Schedule', request.GET.get('uuid'))
        ).data
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def list_sched(request):
    """
        Take in class_uuid (optional), student_uuid (optional).

        If class_name is provided, result will be all schedules for that class.

        If student_uuid is provided, result will be all schedules for all the classes that have that student

        If none, result will be all schedules in db.

        Param class_name takes higher priority
    """

    # class_uuid is provided
    classMeta = request.GET.get('class_uuid')
    if classMeta is not None:
        classMeta = get_by_uuid(ClassMetadata, 'Class', classMeta)
        return Response(ScheduleSerializer(classMeta.schedule_set, many=True).data)

    # student_uuid is provided
    student = request.GET.get('student_uuid')
    if not student is None:
        # Get student
        student = get_by_uuid(CustomUser, 'Student', student)

        # Get classes of student
        classes = student.student_classes.all()

        # Iterate through each class and get its schedules
        data = []
        for c in classes:
            data.extend(ScheduleSerializer(c.schedule_set, many=True).data)

        return Response(data)

    # None are provided
    return Response(ScheduleSerializer(Schedule.objects.all(), many=True).data)
