from django.core.management import BaseCommand
from utils.app_endpoints import get_endpoints


class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('--with_line_break', type=bool, help='Print endpoints with line break')
        parser.add_argument('--endpoints_exclude', type=str, help="The endpoints you don't want to take into account. Example: '/api/commons/example/,/api/commons/example2/'")


    def handle(self, *args, **options):
        endpoints_exclude = options['endpoints_exclude']
        exclude = endpoints_exclude.split(',') if endpoints_exclude else []
        endpoints_list = get_endpoints(exclude=exclude)
        if options["with_line_break"]:
            for endpoint in endpoints_list:
                self.stdout.write(endpoint)
        else:
            print(endpoints_list)