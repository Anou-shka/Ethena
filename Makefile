.PHONY: all schedule charts pdf fetch clean

all: schedule charts pdf  ## rebuild everything from data/

schedule:                 ## reconstruct the ENA vesting schedule
	python scripts/build_unlock_schedule.py

charts: schedule          ## render charts/*.png
	python scripts/make_charts.py

pdf: charts               ## render the report to PDF (needs Chromium via Playwright)
	python scripts/build_pdf.py

fetch:                    ## pull fresh market data into data/raw/
	python scripts/fetch_data.py

clean:
	rm -rf data/raw report/ethena_due_diligence.html
