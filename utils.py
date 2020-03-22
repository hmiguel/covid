from PIL import Image

def merge_images_h(images):  
    widths, heights = zip(*(i.size for i in images))
    total_width, max_height = sum(widths), max(heights)
    merged = Image.new('RGB', (total_width, max_height))
    x_offset = 0
    for im in images:
        merged.paste(im, (x_offset,0))
        x_offset += im.size[0]
    return merged

if __name__ == "__main__":
    #merge_images_h(pages)
    pass