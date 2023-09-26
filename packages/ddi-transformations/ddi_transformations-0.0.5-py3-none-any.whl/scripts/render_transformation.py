import os
import traceback

from jinja2 import Environment, FileSystemLoader


class Transformations:
    TEMPLATE_PATH = template_folder = os.path.dirname(__file__) + "/../resources"
    TEMPLATE_NAME = "transformations_macro.sql"
    FIELDS = "fields"
    SYSTEM_NAME = "systemName"
    FIELD_METADATA = "fieldMetaData"
    COLUMN_NAME = "columnName"
    SO = "SO"

    @staticmethod
    def get_transformation(object_details: dict, job_details: dict, object_type: str):
        print("Start: get_transformation")
        transformation_resp = {}

        try:
            file_loader = FileSystemLoader(Transformations.TEMPLATE_PATH)
            env = Environment(loader=file_loader)
            template = env.get_template(Transformations.TEMPLATE_NAME)
            template.globals.update({'return': Transformations.return_function})

            if object_type == Transformations.SO:
                transformation_resp = Transformations.get_so_transformation(object_details, job_details, template)
            else:
                transformation_resp = Transformations.get_co_transformation(object_details, job_details, template)

        except TypeError as e:
            print(f"TypeError = {traceback.format_exc()}")
            raise

        except IndexError as e:
            print(f"IndexError = {traceback.format_exc()}")
            raise

        except KeyError as e:
            print(f"KeyError = {traceback.format_exc()}")
            raise

        except ValueError as e:
            print(f"ValueError = {traceback.format_exc()}")
            raise

        except AttributeError as e:
            print(f"AttributeError = {traceback.format_exc()}")
            raise

        except IOError as e:
            print(f"IOError = {traceback.format_exc()}")
            raise

        except Exception as e:
            print(f"Exception = {traceback.format_exc()}")
            raise

        print(f"End: get_transformation with response = {transformation_resp}")
        return transformation_resp

    def get_so_transformation(object_details, job_details, template):
        print("Start: get_so_transformation")
        transformation_resp = {}

        for obj_data in object_details:
            for field_data in obj_data[Transformations.FIELDS]:
                column_name = field_data[Transformations.FIELD_METADATA][Transformations.COLUMN_NAME]
                output = template.render(job_details=job_details, sys_name=field_data[Transformations.SYSTEM_NAME],
                                         column_name=field_data[Transformations.FIELD_METADATA][Transformations.COLUMN_NAME]).strip()
                transformation_resp[column_name] = output

        print(f"End: get_so_transformation")
        return transformation_resp

    def get_co_transformation(object_details, job_details, template):
        print("Start: get_co_transformation")
        transformation_resp = {}

        # TODO

        print(f"End: get_co_transformation")
        return transformation_resp

    def return_function(var):
        return var
        
 
if __name__ == '__main__':
    Transformations.get_transformation({}, {}, "SO")

