from rest_framework import viewsets, status
from rest_framework.response import Response
from typing import Type, Optional
from django.db.models import Model


class BaseModelViewSet(viewsets.ModelViewSet):
    """
    Base viewset that provides default CRUD
    operations with standardized responses.
    Supports separate serializers for list and detail views.
    """
    model_class: Optional[Type[Model]] = None
    serializer_class = None
    list_serializer_class = None

    def get_serializer_class(self):
        """
        Return appropriate serializer class based on action.
        """
        if self.action == 'list' and self.list_serializer_class is not None:
            return self.list_serializer_class
        return super().get_serializer_class()

    def get_queryset(self):
        """
        Get the list of items for this viewset.
        """
        if self.model_class is None:
            raise ValueError("model_class must be defined")
        return self.model_class.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Create a new instance with standardized response format.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            return Response(
                {
                    "data": serializer.data,
                    "message": "Created successfully",
                    "status": "success"
                },
                status=status.HTTP_201_CREATED
            )
        return Response(
            {
                "data": None,
                "message": "Validation error",
                "errors": serializer.errors,
                "status": "error"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def update(self, request, *args, **kwargs):
        """
        Update an instance with standardized response format.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(
                {
                    "data": serializer.data,
                    "message": "Updated successfully",
                    "status": "success"
                }
            )
        return Response(
            {
                "data": None,
                "message": "Validation error",
                "errors": serializer.errors,
                "status": "error"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    def destroy(self, request, *args, **kwargs):
        """
        Delete an instance with standardized response format.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {
                "data": None,
                "message": "Deleted successfully",
                "status": "success"
            },
            status=status.HTTP_200_OK
        )

    def list(self, request, *args, **kwargs):
        """
        List instances with standardized response format.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "data": serializer.data,
                "message": "Retrieved successfully",
                "status": "success"
            }
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve an instance with standardized response format.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(
            {
                "data": serializer.data,
                "message": "Retrieved successfully",
                "status": "success"
            }
        )
