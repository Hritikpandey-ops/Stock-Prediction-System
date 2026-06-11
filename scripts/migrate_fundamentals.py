"""
Migration script to update fundamentals table with new columns
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from config.database import SessionLocal, engine
from sqlalchemy import text

def migrate():
    session = SessionLocal()
    
    print("Starting migration...")
    
    try:
        # Drop the old table
        print("Dropping old fundamentals table...")
        session.execute(text("DROP TABLE IF EXISTS fundamentals CASCADE;"))
        session.commit()
        print("✓ Old table dropped")
        
        # Create new table with all columns
        print("Creating new fundamentals table...")
        
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS fundamentals (
            id BIGSERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            report_date TIMESTAMPTZ NOT NULL,
            period_type VARCHAR(20) NOT NULL,
            
            market_cap BIGINT,
            current_price DECIMAL(12, 2),
            fifty_two_week_high DECIMAL(12, 2),
            fifty_two_week_low DECIMAL(12, 2),
            dividend_yield DECIMAL(5, 2),
            shares_outstanding BIGINT,
            
            pe_ratio DECIMAL(10, 2),
            pb_ratio DECIMAL(10, 2),
            peg_ratio DECIMAL(10, 2),
            ev_ebitda DECIMAL(10, 2),
            industry_pe DECIMAL(10, 2),
            
            eps DECIMAL(10, 2),
            roe DECIMAL(5, 2),
            roce DECIMAL(5, 2),
            net_profit_margin DECIMAL(5, 2),
            operating_margin DECIMAL(5, 2),
            ebitda BIGINT,
            
            revenue BIGINT,
            revenue_growth_1y DECIMAL(5, 2),
            revenue_growth_3y DECIMAL(5, 2),
            revenue_growth_5y DECIMAL(5, 2),
            
            net_profit BIGINT,
            profit_growth_1y DECIMAL(5, 2),
            profit_growth_3y DECIMAL(5, 2),
            profit_growth_5y DECIMAL(5, 2),
            
            eps_growth_1y DECIMAL(5, 2),
            eps_growth_3y DECIMAL(5, 2),
            eps_growth_5y DECIMAL(5, 2),
            
            total_debt BIGINT,
            debt_to_equity DECIMAL(5, 2),
            interest_coverage DECIMAL(10, 2),
            
            current_assets BIGINT,
            current_liabilities BIGINT,
            current_ratio DECIMAL(5, 2),
            cash_and_equivalents BIGINT,
            free_cash_flow BIGINT,
            operating_cash_flow BIGINT,
            
            promoter_holding DECIMAL(5, 2),
            fii_holding DECIMAL(5, 2),
            dii_holding DECIMAL(5, 2),
            public_holding DECIMAL(5, 2),
            
            sector VARCHAR(100),
            industry VARCHAR(100),
            company_name VARCHAR(200),
            
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (symbol, report_date, period_type)
        );
        """
        
        session.execute(text(create_table_sql))
        session.commit()
        print("✓ New table created")
        
        # Create index
        session.execute(text("CREATE INDEX IF NOT EXISTS idx_fundamentals_symbol_date ON fundamentals (symbol, report_date DESC);"))
        session.commit()
        print("✓ Index created")
        
        # Add the unique constraint with the correct name
        session.execute(text("""
            ALTER TABLE fundamentals 
            ADD CONSTRAINT uq_symbol_report_period 
            UNIQUE (symbol, report_date, period_type);
        """))
        session.commit()
        print("✓ Unique constraint created")
        
        print("\n✅ Migration complete!")
        print("The fundamentals table now has all the required columns.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error during migration: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    migrate()