from fastapi import FastAPI, HTTPException, File, UploadFile, Response, Form
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import os
import cairosvg
from time import time
from typing import Optional
from loguru import logger
from modules.pcgenerator import PCGenerator, calibrate

app = FastAPI()


# Define Pydantic model for the PCGenerator form
class PCGeneratorForm(BaseModel):
    test: Optional[str] = None
    blank: Optional[str] = None
    fill: Optional[str] = None
    png: Optional[str] = None


# Endpoint implementations


@app.get("/", response_class=HTMLResponse)
async def index_get():
    logger.info("Serving the index page")
    filepath = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "./templates", "index.html"
    )
    return FileResponse(filepath)


@app.get("/calculator/", response_class=HTMLResponse)
async def calculator_get():
    logger.info("Serving the calculator page")
    filepath = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "./templates", "calculator.html"
    )
    return FileResponse(filepath)


@app.get("/pcgenerator/", response_class=HTMLResponse)
async def pcgenerator_get():
    logger.info("Serving the PC Generator page")
    filepath = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "./templates", "pcgenerator.html"
    )
    return FileResponse(filepath)


@app.post("/pcgenerator/")
async def pcgenerator_post(
    test: Optional[str] = Form(None),
    blank: Optional[str] = Form(None),
    fill: Optional[str] = Form(None),
    machine: str = Form(...),  # Using Form(...) indicates a required field
    vert: float = Form(...),
    png: Optional[str] = Form(None),
    upfile: UploadFile = File(...),
):
    try:
        logger.info("Processing PC Generator request")
        file_content = await upfile.read()

        calibrate_only = test == "test"
        is_blank = blank == "blank"
        is_solid_fill = fill == "fill"

        if calibrate_only:
            logger.debug("Calibrate only request")
            result = calibrate()
            filename = "calibrate.svg"
        else:
            try:
                if file_content and len(file_content) > 8000:
                    logger.warning("File size exceeds limit")
                    raise HTTPException(
                        status_code=413, detail="File size exceeds limit."
                    )

                pc_generator = PCGenerator(
                    handler=file_content.decode("utf-8"),
                    data=file_content,
                    machine_id=machine,
                    vert_repeat=vert,
                    is_blank=is_blank,
                    is_solid_fill=is_solid_fill,
                )
                result = pc_generator.generate()
                now = int(time())
                filename = f"punchcard-{now}.{png if png else 'svg'}"

                if png:
                    result = cairosvg.svg2png(bytestring=result.encode())
            except Exception as exc:
                logger.error(f"Encountered exception {exc}")
                raise Exception from exc
        logger.info("Successfully processed PC Generator request")
        return Response(
            content=result,
            media_type="image/png" if png else "image/svg+xml",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        logger.error(f"Error processing PC Generator request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")
