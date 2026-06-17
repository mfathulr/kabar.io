-- Main migration for the Neon news storage.
-- Keep this as the canonical schema file.
-- If you add a new feature later, create a temporary numbered file first,
-- then merge or squash it back into this main migration when you're ready.

CREATE TABLE IF NOT EXISTS news_articles (
    article_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    source_id TEXT,
    source_url TEXT,
    country TEXT NOT NULL DEFAULT 'id',
    category TEXT NOT NULL,
    language TEXT,
    published_at TIMESTAMPTZ,
    fetched_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at_wib TIMESTAMPTZ,
    domain TEXT,
    sentiment TEXT NOT NULL DEFAULT 'unknown',
    sentiment_confidence DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (sentiment_confidence >= 0 AND sentiment_confidence <= 1),
    sentiment_reason TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_news_articles_category_published_at
    ON news_articles (category, published_at DESC);

CREATE INDEX IF NOT EXISTS idx_news_articles_fetched_at
    ON news_articles (fetched_at DESC);

CREATE INDEX IF NOT EXISTS idx_news_articles_source_id
    ON news_articles (source_id);

CREATE OR REPLACE FUNCTION set_news_articles_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_news_articles_updated_at ON news_articles;

CREATE TRIGGER trg_news_articles_updated_at
BEFORE UPDATE ON news_articles
FOR EACH ROW
EXECUTE FUNCTION set_news_articles_updated_at();
