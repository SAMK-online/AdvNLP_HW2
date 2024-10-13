import requests
from typing import AnyStr
from gentopia.tools.basetool import *
from PyPDF2 import PdfReader
import io

class ReadPDFArgs(BaseModel):
    file_path_or_url: str = Field(..., description="The path to the PDF file or a URL to a PDF.")

class ReadPDF(BaseTool):
    name = "read_pdf"
    args_schema: Optional[Type[BaseModel]] = ReadPDFArgs
    description: str = "Read a PDF file or URL and extract its text content."

    def _run(self, file_path_or_url: str) -> AnyStr:
        try:
            if file_path_or_url.startswith(('http://', 'https://')):
                response = requests.get(file_path_or_url)
                response.raise_for_status()  
                pdf_file = io.BytesIO(response.content)
            else:
                pdf_file = open(file_path_or_url, 'rb')

            pdf = PdfReader(pdf_file)
            text = ""
            for page in pdf.pages:
                text += page.extract_text()

            if not file_path_or_url.startswith(('http://', 'https://')):
                pdf_file.close()

            return text[:1000] 
        except requests.exceptions.RequestException as e:
            return f"Error downloading the PDF: {str(e)}"
        except Exception as e:
            return f"An error occurred while reading the PDF: {str(e)}"

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError