# Braillest Tooling

![A stack of flyers created by Braillest.](docs/img/braillest-flyer-zoom-ad.png)

# Table of Contents

- [Welcome](#welcome)
- [Getting Started](#getting-started)
- [Manifesto](#manifesto)
- [Usage](#usage)
- [Samples](#samples)
- [Embossing Process](#embossing-process)
- [Repair Process](#repair-process)
- [Standard](#standard)

# Welcome

Howdy! 🤠 Welcome to the primary tooling repo of the Braillest project. This repo contains all the scripts needed to:
- Source sample books from the gutenberg press website and convert them into their standalone texts.
- Translate texts into braille while performing back translations to compare against.
- Perform formatting and pagination operations to comply with constraints of printing format.
- Generate the produced braille pages into mold STLs for slicing and printing.

# Getting Started

1. Download and install [Docker](https://www.docker.com/).
2. Clone this repo. `git clone git@github.com:Braillest/tooling.git`
3. Navigate to the root of the project in the terminal and run `docker compose up -d`
4. Enter the container `docker exec -it braillest_tooling bash`
5. Authenticate gh `gh auth login`. Follow the instructions to authenticate. Add PAT with the following permissions:

```
Administration: Read/Write
Contents: Read/Write
Metadata: Read
Pull requests: Read/Write
```

# Manifesto

![Braillest is an open-source braille production project created to dramatically lower the cost and barriers of producing braille literature. Founded in early 2025 by software engineer and accessibility advocate Lewis Brown, the project replaces traditional, expensive braille embossing methods with 3D-printed, reusable page molds. Conventional braille production frequently costs more than $1.50 per page, limiting access for schools, libraries, nonprofits, and individuals. Braillest disrupts this model by shifting cost from per-page output to reusable molds. A single mold costing roughly $1.00 in filament can emboss hundreds of pages, driving the effective per-page cost well below industry norms as volume increases. Braillest's software converts text into standardized braille and generates highly precise digital molds that emboss entire pages at once. This process produces clean, consistent, and sharply defined braille dots, ensuring reliable tactile readability. Because molds are digital and reusable, content can be reproduced without repeated translation or setup. A uniquely powerful feature of Braillest is repairability. If a page becomes worn or damaged, it can be re-embossed using the original mold rather than recreated from scratch, extending the lifespan of braille materials and reducing long-term costs. Built on open-source principles and accessible manufacturing tools, Braillest decentralizes braille production and empowers communities to create affordable, high-quality tactile materials redefining braille as scalable, precise, and sustainable.](docs/img/braillest-executive-summary-50-resize.jpg)

# Usage

## From within the container:

- Download books: `python download_books.py`

## From the host at the root of the project:

- Generate molds: `./scripts/generate_all_page_molds.sh <text_file>`
> ex) `./scripts/generate_all_page_molds.sh "./data/1-texts/Dracula by Bram Stoker.txt"`

# Samples

![An embossing sample using depth of field to focus on braille dots in the center of the page.](docs/img/samples/20250821_170315.jpg)
![A closeup of braille printed onto light blue paper.](docs/img/samples/20250830_175045.jpg)
![Another closeup of braille, taken at a diagonal angle.](docs/img/samples/20251228_190157.jpg)
![Another angle of the previous image, but showcasing the impressions of the braille dots.](docs/img/samples/20251228_190216.jpg)
![A closeup of the interlocking geometry of the positive and negative molds.](docs/img/samples/20250818_144433.jpg)

# Embossing Process

## Print Universal Negative
![A photo of a printed universal negative mold.](docs/img/embossing/1-negative.jpg)

## Print Positive
![A photo of a printed positive mold.](docs/img/embossing/2-positive.jpg)

## Load Mold
![A photo of a loaded mold.](docs/img/embossing/3-load-mold.jpg)

## Mold Sandwich
![A photo of a mold sandwich.](docs/img/embossing/4-mold-sandwich.jpg)

## Calibrate Roller Press
![A photo of a calibrated roller press.](docs/img/embossing/5-calibrate-roller-press.jpg)

## Load Mold Sandwich
![A photo of a mold sandwich being loaded into the roller press.](docs/img/embossing/6-load-mold-sandwich.jpg)

## Remove Mold Sandwich
![A photo of mold sandwich being removed from the roller press.](docs/img/embossing/7-remove-pressed-molds.jpg)

## Remove Negative
![A photo of a negative mold being removed, revealing the embossed paper.](docs/img/embossing/8-remove-negative.jpg)

## Sample Result
![A photo of a sample result.](docs/img/embossing/9-sample-result.jpg)

## Stack of Flyers
![A photo of a stack of flyers.](docs/img/embossing/9-stack-of-flyers.jpg)

# Repair Process

## Sample
![An embossed flyer that was selected to be damaged.](docs/img/repair/1-sample.jpg)

## Damaged
![A photo of the damaged flyer.](docs/img/repair/2-damaged.jpg)

## Load Damaged Mold
![A photo of the damaged mold being loaded into a mold sandwich.](docs/img/repair/3-load-damaged-mold.jpg)

## Mold Sandwich Roller
![A photo of the mold sandwich being pressed with a hand roller.](docs/img/repair/4-mold-sandwich-roller.jpg)

## Remove
![A photo of the negative mold removed, showing the repaired braille.](docs/img/repair/5-remove.jpg)

# Standard

![The braillest format was designed specifically for US letter size paper using 3 ring binding and achieves a cell density of 32 columns and 26 rows, giving a total of 832 cells per page. We think our proposed standard meets a good middle ground between density vs readability. Cell column spacing of 2.5mm, dot diameter of 1.7mm, dot height of 0.6mm, cell width of 6mm, cell height of 10mm.](docs/img/braillest-standard.jpg)
