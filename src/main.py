"""Main application for CD Booklet OCR"""

import argparse
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ocr_processor import BookletOCR
from image_utils import get_image_files, load_image, validate_directory
from markdown_generator import ObsidianMarkdownGenerator
import config


def process_booklet(image_dir, output_dir="output", verbose=True):
    """
    Process all images in a directory and generate Obsidian markdown

    Args:
        image_dir: Path to directory containing images
        output_dir: Output directory for markdown file
        verbose: Show progress messages
    """
    try:
        # Validate input directory
        num_images = validate_directory(image_dir)
        if verbose:
            print(f"Found {num_images} images in {image_dir}")

        # Get sorted image files
        image_files = get_image_files(image_dir)

        # Initialize OCR processor
        if verbose:
            print("Initializing OCR processor...")

        ocr = BookletOCR(lang=config.OCR_LANGUAGE, use_gpu=config.OCR_USE_GPU)

        # Initialize markdown generator
        markdown_gen = ObsidianMarkdownGenerator(
            frontmatter=config.OBSIDIAN_FRONTMATTER,
            enable_callouts=config.ENABLE_CALLOUTS,
        )

        # Process each image
        if verbose:
            print("\nProcessing images...")

        images_data = []

        for idx, image_path in enumerate(image_files, 1):
            if verbose:
                print(f"[{idx}/{len(image_files)}] Processing: {image_path.name}")

            # Load image
            image = load_image(image_path)
            if image is None:
                images_data.append(
                    {"image_path": str(image_path), "error": "Failed to load image"}
                )
                continue

            # Process with OCR
            try:
                ocr_results = ocr.process_image(image)

                grouped_results = ocr.group_text_lines(ocr_results, y_threshold=15)

                for text_info in grouped_results:
                    text_info["styles"] = ocr.classify_text_style(
                        text_info, min_heading_size=config.MIN_HEADING_FONT_SIZE
                    )

                images_data.append(
                    {
                        "image_path": str(image_path),
                        "results": grouped_results,
                        "num_texts": len(grouped_results),
                    }
                )

                if verbose:
                    print(f"  Detected {len(grouped_results)} text lines")

            except Exception as e:
                if verbose:
                    print(f"  ✗ Error: {e}")
                images_data.append({"image_path": str(image_path), "error": str(e)})

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Generate output path
        source_name = Path(image_dir).name
        output_path = os.path.join(output_dir, f"{source_name}.md")

        # Generate markdown
        if verbose:
            print(f"\nGenerating Obsidian Markdown...")

        markdown_gen.generate(images_data, output_path, image_dir)

        if verbose:
            print(f"\n✓ Successfully generated: {output_path}")
            print(f"✓ Processed {len(images_data)} pages")

            total_texts = sum(
                img.get("num_texts", 0) for img in images_data if "num_texts" in img
            )
            print(f"✓ Total text blocks detected: {total_texts}")

        return output_path

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="CD Booklet OCR - Convert scanned booklets to Obsidian Markdown"
    )

    parser.add_argument("input_dir", help="Directory containing scanned booklet images")

    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Output directory for markdown file (default: output)",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Show detailed progress messages"
    )

    parser.add_argument(
        "--no-footmatter", action="store_true", help="Disable Obsidian frontmatter"
    )

    parser.add_argument(
        "--no-callouts", action="store_true", help="Disable Obsidian callouts"
    )

    args = parser.parse_args()

    # Override config if flags provided
    if args.no_footmatter:
        config.OBSIDIAN_FRONTMATTER = False

    if args.no_callouts:
        config.ENABLE_CALLOUTS = False

    # Process booklet
    output_file = process_booklet(
        args.input_dir,
        output_dir=args.output,
        verbose=True if not args.verbose else args.verbose,
    )

    if output_file:
        print(f"\n✅ Done! Open the file in Obsidian: {output_file}")
        return 0
    else:
        print(f"\n❌ Failed to process booklet")
        return 1


if __name__ == "__main__":
    sys.exit(main())
