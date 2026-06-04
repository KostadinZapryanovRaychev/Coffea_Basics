from pathlib import Path
import sys
import logging

logging.basicConfig(
    level=logging.INFO,   # <- changed
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)

logger = logging.getLogger(__name__)

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))


def get_path():
    try:
        project_path = "/eos/cms/store/user/mileva/bsm3g/NANOAODSIM/ZprimeTo2Tau-2Jets_M-250_TuneCP5_13p6TeV_madgraphMLM-pythia8/Run3Summer23_NANOAODv12/250716_092714/0000/"
        path = Path(project_path)
        return path

    except Exception as e:
        logger.error(
            f"\n[ERROR] Unexpected error while getting path\n"
            f"Exception type: {type(e).__name__}\n"
            f"Details: {str(e)}\n"
        )

    return None


def list_files_in_directory(directory: Path):
    try:
        if not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return []

        if not directory.is_dir():
            logger.warning(f"Path is not a directory: {directory}")
            return []

        files = list(directory.iterdir())

        if not files:
            logger.warning(f"Directory is empty: {directory}")
            return []

        logger.info(f"\nFiles inside: {directory}\n")

        for file in files:
            if file.is_dir():
                logger.info(f"[DIR ] {file.name}")
            else:
                logger.info(f"[FILE] {file.name}")

        return files

    except Exception as e:
        logger.error(
            f"\n[ERROR] Unexpected error while listing files\n"
            f"Directory: {directory}\n"
            f"Exception type: {type(e).__name__}\n"
            f"Details: {str(e)}\n"
        )

        return []


def main():
    try:
        path = get_path()

        logger.info(f"Project path: {path}")

        list_files_in_directory(path)

    except Exception as e:
        logger.error(
            f"\n[ERROR] Unexpected error in main()\n"
            f"Exception type: {type(e).__name__}\n"
            f"Details: {str(e)}\n"
        )


if __name__ == "__main__":
    main()