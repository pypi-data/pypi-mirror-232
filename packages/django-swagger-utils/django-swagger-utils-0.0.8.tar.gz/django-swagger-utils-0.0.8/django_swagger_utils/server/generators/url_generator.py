from django.urls import path

urlpatterns = []


class GenerateURLPatterns(object):
    def __init__(self, app_name, paths):
        self.app_name = app_name
        self.paths = paths

    def generate_url_patterns(self):
        import_statement = "from {} import views".format(self.app_name)
        exec(import_statement)

        for path, operations in self.paths.items():
            for http_method, operation in operations.items():
                operation_id = operation.get('operationId')

                if http_method == 'get':
                    urlpatterns.append(
                        path(path, getattr(views, 'get_handler_function'), name=operation_id)
                    )
                elif http_method == 'post':
                    urlpatterns.append(
                        path(path, getattr(views, 'post_handler_function'), name=operation_id)
                    )
