from qx_base.qx_user.viewsets import UserViewSet as BaseUserViewSet


class UserViewSet(BaseUserViewSet):

    def get_serializer_class(self):
        if self.action == 'signin':
            return
        return super().get_serializer_class()
