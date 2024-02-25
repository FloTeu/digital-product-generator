from typing import List
from digiprod_gen.backend.models.mba import MBAProduct

def mba_products_overview_html_str(products: List[MBAProduct], columns: int = 5) -> str:
    # Start the HTML with a table
    html_str = "<table style='width: 100%; border-collapse: collapse;'>\n"

    # Initialize counter for product placement
    product_counter = 0

    # Loop through the products and create table rows and cells
    for i, product in enumerate(products):
        # Every time the counter is at the start of a new row, create a new table row
        if product_counter % columns == 0:
            if product_counter != 0:
                # Close the previous row if it's not the first product
                html_str += "</tr>\n"
            # Start a new row
            html_str += "<tr>\n"

        # Table cell for the product
        html_str += f"""<td style='border: 3px solid #000; padding: 10px; vertical-align: top;'>
            <img src='{product.image_url}' alt='{product.title}' style='width: 100%; height: auto; display: block;'>
            <div style='text-align: center;'>
                <p style='color: #333; font-size: 9px;'>Nr. <b>{i}</b></p>
                {f"<p style='color: #333; font-size: 9px;'><b>{product.brand}</b></p>" if product.brand else ''}
                <a href='{product.product_url}' target='_blank' style='text-decoration: none; color: #333;'>
                    <p style='margin: 10px 0; font-size: 9px;'>{product.title}</p>
                </a>
                <p style='color: #555; font-size: 9px;'><b>${'{:.2f}'.format(product.price) if product.price else 'N/A'}</b></p>
            </div>
        </td>\n"""

        # Increment product counter
        product_counter += 1

    # Close the last row and table tags
    html_str += "</tr>\n</table>"

    return html_str