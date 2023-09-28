from studio.app.common.core.utils.filepath_creater import join_filepath
from studio.app.common.core.workflow.workflow import OutputPath, OutputType
from studio.app.common.dataclass.base import BaseData


class HTMLData(BaseData):
    def __init__(self, data, file_name="html"):
        super().__init__(file_name)
        self.data = data

    def save_json(self, json_dir):
        self.json_path = join_filepath([json_dir, f"{self.file_name}.html"])

        with open(self.json_path, "w") as f:
            f.write(self.data)

    @property
    def output_path(self) -> OutputPath:
        return OutputPath(path=self.json_path, type=OutputType.HTML)
