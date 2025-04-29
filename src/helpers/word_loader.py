import pandas as pd
from src.config import EXCEL_FILES
from src.helpers.logger import get_logger

logger = get_logger("WordLoader")

def load_words_for_level(level):
    try:
        file = EXCEL_FILES[level]
        df = pd.read_excel(file)
        # Sütun adlarını temizle ve normalize et
        clean_columns = {col: col.strip().lower().replace(" ", "") for col in df.columns}
        df.rename(columns=clean_columns, inplace=True)
        logger.info(f"Excel columns in {file}: {list(df.columns)}")
        possible_columns = ['terms']
        word_col = None
        for col in possible_columns:
            if col in df.columns:
                word_col = col
                break
        if word_col is None:
            logger.error(f"None of the expected word columns found in {file}. Columns: {list(df.columns)}")
            raise KeyError(f"None of the expected word columns found in {file}. Please use one of: {possible_columns}")
        words = df[word_col].dropna().tolist()
        logger.info(f"Loaded {len(words)} words for level {level} from {file}")
        return words
    except Exception as e:
        logger.exception(f"Failed to load words for level {level}")
        raise 