from bs4 import BeautifulSoup
from dataclasses import dataclass, field

@dataclass
class ScoresheetData:
    image_color_0: list = field(default_factory=list)# = [0, 0, 0]
    image_color_1: list = field(default_factory=list)# = [0, 0, 0]
    orientation_score: float = 0
    ornt_img_low_0_0: str = ""
    ornt_img_low_0_1: str = ""
    ornt_vis_low_0_ext: str = ""
    ornt_vis_low_0_ref: str = ""
    ornt_low_0_error: float = 0
    ornt_img_low_1_0: str = ""
    ornt_img_low_1_1: str = ""
    ornt_vis_low_1_ext: str = ""
    ornt_vis_low_1_ref: str = ""
    ornt_low_1_error: float = 0
    ornt_img_low_2_0: str = ""
    ornt_img_low_2_1: str = ""
    ornt_vis_low_2_ext: str = ""
    ornt_vis_low_2_ref: str = ""
    ornt_low_2_error: float = 0
    ornt_img_high_0_0: str = ""
    ornt_img_high_0_1: str = ""
    ornt_vis_high_0_ext: str = ""
    ornt_vis_high_0_ref: str = ""
    ornt_high_0_error: float = 0
    ornt_img_high_1_0: str = ""
    ornt_img_high_1_1: str = ""
    ornt_vis_high_1_ext: str = ""
    ornt_vis_high_1_ref: str = ""
    ornt_high_1_error: float = 0
    ornt_img_high_2_0: str = ""
    ornt_img_high_2_1: str = ""
    ornt_vis_high_2_ext: str = ""
    ornt_vis_high_2_ref: str = ""
    ornt_high_2_error: float = 0
    # position_score: float = 0
    # pos_img_low_0_0: str = ""
    # pos_img_low_0_1: str = ""
    # pos_img_low_1_0: str = ""
    # pos_img_low_1_1: str = ""
    # pos_img_low_2_0: str = ""
    # pos_img_low_2_1: str = ""
    # pos_img_high_0_0: str = ""
    # pos_img_high_0_1: str = ""
    # pos_img_high_1_0: str = ""
    # pos_img_high_1_1: str = ""
    # pos_img_high_2_0: str = ""
    # pos_img_high_2_1: str = ""


@dataclass
class CompareScoresheetData:
    image_color_0: list = field(default_factory=list)# = [0, 0, 0]
    image_color_1: list = field(default_factory=list)# = [0, 0, 0]
    orientation_score_0: float = 0
    orientation_score_1: float = 0
    ornt_img_low_0_0: str = ""
    ornt_img_low_0_1: str = ""
    ornt_vis_low_0_0: str = ""
    ornt_vis_low_0_1: str = ""
    ornt_low_0_error0: float = 0
    ornt_low_0_error1: float = 0
    ornt_img_low_1_0: str = ""
    ornt_img_low_1_1: str = ""
    ornt_vis_low_1_0: str = ""
    ornt_vis_low_1_1: str = ""
    ornt_low_1_error0: float = 0
    ornt_low_1_error1: float = 0
    ornt_img_high_0_0: str = ""
    ornt_img_high_0_1: str = ""
    ornt_vis_high_0_0: str = ""
    ornt_vis_high_0_0: str = ""
    ornt_high_0_error0: float = 0
    ornt_high_0_error1: float = 0
    ornt_img_high_1_0: str = ""
    ornt_img_high_1_1: str = ""
    ornt_vis_high_1_0: str = ""
    ornt_vis_high_1_1: str = ""
    ornt_high_1_error0: float = 0
    ornt_high_1_error1: float = 0
    # position_score: float = 0
    # pos_img_low_0_0: str = ""
    # pos_img_low_0_1: str = ""
    # pos_img_low_1_0: str = ""
    # pos_img_low_1_1: str = ""
    # pos_img_low_2_0: str = ""
    # pos_img_low_2_1: str = ""
    # pos_img_high_0_0: str = ""
    # pos_img_high_0_1: str = ""
    # pos_img_high_1_0: str = ""
    # pos_img_high_1_1: str = ""
    # pos_img_high_2_0: str = ""
    # pos_img_high_2_1: str = ""

def create_scoresheet(scoresheet_data, output_folder):

    with open('scoresheet-template.html') as html_file:
        soup = BeautifulSoup(html_file.read(), features='html.parser')

        col0 = [int(x * 255) for x in scoresheet_data.image_color_0]
        col1 = [int(x * 255) for x in scoresheet_data.image_color_1]
        style_str_0 = f"border: 5px solid rgb({col0[0]}, {col0[1]}, {col0[2]});"
        style_str_1 = f"border: 5px solid rgb({col1[0]}, {col1[1]}, {col1[2]});"
        
        soup.find(id='orientation_score').string.replace_with(str(scoresheet_data.orientation_score))

        # images
        soup.find(id='ornt_img_low_0_0')['src'] = scoresheet_data.ornt_img_low_0_0        
        soup.find(id='ornt_img_low_0_1')['src'] = scoresheet_data.ornt_img_low_0_1
        soup.find(id='ornt_img_low_1_0')['src'] = scoresheet_data.ornt_img_low_1_0
        soup.find(id='ornt_img_low_1_1')['src'] = scoresheet_data.ornt_img_low_1_1
        soup.find(id='ornt_img_low_2_0')['src'] = scoresheet_data.ornt_img_low_2_0
        soup.find(id='ornt_img_low_2_1')['src'] = scoresheet_data.ornt_img_low_2_1

        soup.find(id='ornt_img_high_0_0')['src'] = scoresheet_data.ornt_img_high_0_0
        soup.find(id='ornt_img_high_0_1')['src'] = scoresheet_data.ornt_img_high_0_1
        soup.find(id='ornt_img_high_1_0')['src'] = scoresheet_data.ornt_img_high_1_0
        soup.find(id='ornt_img_high_1_1')['src'] = scoresheet_data.ornt_img_high_1_1
        soup.find(id='ornt_img_high_2_0')['src'] = scoresheet_data.ornt_img_high_2_0
        soup.find(id='ornt_img_high_2_1')['src'] = scoresheet_data.ornt_img_high_2_1

        soup.find(id='ornt_img_low_0_0')['title'] = scoresheet_data.ornt_img_low_0_0        
        soup.find(id='ornt_img_low_0_1')['title'] = scoresheet_data.ornt_img_low_0_1
        soup.find(id='ornt_img_low_1_0')['title'] = scoresheet_data.ornt_img_low_1_0
        soup.find(id='ornt_img_low_1_1')['title'] = scoresheet_data.ornt_img_low_1_1
        soup.find(id='ornt_img_low_2_0')['title'] = scoresheet_data.ornt_img_low_2_0
        soup.find(id='ornt_img_low_2_1')['title'] = scoresheet_data.ornt_img_low_2_1

        soup.find(id='ornt_img_high_0_0')['title'] = scoresheet_data.ornt_img_high_0_0
        soup.find(id='ornt_img_high_0_1')['title'] = scoresheet_data.ornt_img_high_0_1
        soup.find(id='ornt_img_high_1_0')['title'] = scoresheet_data.ornt_img_high_1_0
        soup.find(id='ornt_img_high_1_1')['title'] = scoresheet_data.ornt_img_high_1_1
        soup.find(id='ornt_img_high_2_0')['title'] = scoresheet_data.ornt_img_high_2_0
        soup.find(id='ornt_img_high_2_1')['title'] = scoresheet_data.ornt_img_high_2_1

        # image borders -> for easily telling them apart in the 3D visualization.
        soup.find(id='ornt_img_low_0_0')['style'] = style_str_0
        soup.find(id='ornt_img_low_0_1')['style'] = style_str_1
        soup.find(id='ornt_img_low_1_0')['style'] = style_str_0
        soup.find(id='ornt_img_low_1_1')['style'] = style_str_1
        soup.find(id='ornt_img_low_2_0')['style'] = style_str_0
        soup.find(id='ornt_img_low_2_1')['style'] = style_str_1

        soup.find(id='ornt_img_high_0_0')['style'] = style_str_0
        soup.find(id='ornt_img_high_0_1')['style'] = style_str_1
        soup.find(id='ornt_img_high_1_0')['style'] = style_str_0
        soup.find(id='ornt_img_high_1_1')['style'] = style_str_1
        soup.find(id='ornt_img_high_2_0')['style'] = style_str_0
        soup.find(id='ornt_img_high_2_1')['style'] = style_str_1

        # 3d visualizations
        soup.find(id='ornt_vis_low_0_ext')['src'] = scoresheet_data.ornt_vis_low_0_ext
        soup.find(id='ornt_vis_low_0_ref')['src'] = scoresheet_data.ornt_vis_low_0_ref
        soup.find(id='ornt_vis_low_1_ext')['src'] = scoresheet_data.ornt_vis_low_1_ext
        soup.find(id='ornt_vis_low_1_ref')['src'] = scoresheet_data.ornt_vis_low_1_ref
        soup.find(id='ornt_vis_low_2_ext')['src'] = scoresheet_data.ornt_vis_low_2_ext
        soup.find(id='ornt_vis_low_2_ref')['src'] = scoresheet_data.ornt_vis_low_2_ref

        soup.find(id='ornt_vis_high_0_ext')['src'] = scoresheet_data.ornt_vis_high_0_ext
        soup.find(id='ornt_vis_high_0_ref')['src'] = scoresheet_data.ornt_vis_high_0_ref
        soup.find(id='ornt_vis_high_1_ext')['src'] = scoresheet_data.ornt_vis_high_1_ext
        soup.find(id='ornt_vis_high_1_ref')['src'] = scoresheet_data.ornt_vis_high_1_ref
        soup.find(id='ornt_vis_high_2_ext')['src'] = scoresheet_data.ornt_vis_high_2_ext
        soup.find(id='ornt_vis_high_2_ref')['src'] = scoresheet_data.ornt_vis_high_2_ref
        
        # errors
        soup.find(id='ornt_low_0_error').string.replace_with(str(scoresheet_data.ornt_low_0_error))
        soup.find(id='ornt_low_1_error').string.replace_with(str(scoresheet_data.ornt_low_1_error))
        soup.find(id='ornt_low_2_error').string.replace_with(str(scoresheet_data.ornt_low_2_error))
        soup.find(id='ornt_high_0_error').string.replace_with(str(scoresheet_data.ornt_high_0_error))
        soup.find(id='ornt_high_1_error').string.replace_with(str(scoresheet_data.ornt_high_1_error))
        soup.find(id='ornt_high_2_error').string.replace_with(str(scoresheet_data.ornt_high_2_error))

        # soup.find(id='position_score').string.replace_with(scoresheet_data.position_score)

        # soup.find(id='pos_img_low_0_0')['src'] = scoresheet_data.pos_img_low_0_0
        # soup.find(id='pos_img_low_0_1')['src'] = scoresheet_data.pos_img_low_0_1
        # soup.find(id='pos_img_low_1_0')['src'] = scoresheet_data.pos_img_low_1_0
        # soup.find(id='pos_img_low_1_1')['src'] = scoresheet_data.pos_img_low_1_1
        # soup.find(id='pos_img_low_2_0')['src'] = scoresheet_data.pos_img_low_2_0
        # soup.find(id='pos_img_low_2_1')['src'] = scoresheet_data.pos_img_low_2_1

        # soup.find(id='pos_img_high_0_0')['src'] = scoresheet_data.pos_img_high_0_0
        # soup.find(id='pos_img_high_0_1')['src'] = scoresheet_data.pos_img_high_0_1
        # soup.find(id='pos_img_high_1_0')['src'] = scoresheet_data.pos_img_high_1_0
        # soup.find(id='pos_img_high_1_1')['src'] = scoresheet_data.pos_img_high_1_1
        # soup.find(id='pos_img_high_2_0')['src'] = scoresheet_data.pos_img_high_2_0
        # soup.find(id='pos_img_high_2_1')['src'] = scoresheet_data.pos_img_high_2_1

        # Store prettified version of modified html
        new_text = soup.prettify()

    # Write new contents to test.html
    with open(f'{output_folder}/scoresheet.html', mode='w') as new_html_file:
        new_html_file.write(new_text)

    print(f"Written scoresheet file to: {output_folder}/scoresheet.html")


def create_compare_sheet(scoresheet_data, output_folder):

    with open('scoresheet-template-compare.html') as html_file:
        soup = BeautifulSoup(html_file.read(), features='html.parser')

        col0 = [int(x * 255) for x in scoresheet_data.image_color_0]
        col1 = [int(x * 255) for x in scoresheet_data.image_color_1]
        style_str_0 = f"border: 5px solid rgb({col0[0]}, {col0[1]}, {col0[2]});"
        style_str_1 = f"border: 5px solid rgb({col1[0]}, {col1[1]}, {col1[2]});"
        
        soup.find(id='orientation_score_0').string.replace_with(str(scoresheet_data.orientation_score_0))
        soup.find(id='orientation_score_1').string.replace_with(str(scoresheet_data.orientation_score_1))

        # images
        soup.find(id='ornt_img_low_0_0')['src'] = scoresheet_data.ornt_img_low_0_0        
        soup.find(id='ornt_img_low_0_1')['src'] = scoresheet_data.ornt_img_low_0_1
        soup.find(id='ornt_img_low_1_0')['src'] = scoresheet_data.ornt_img_low_1_0
        soup.find(id='ornt_img_low_1_1')['src'] = scoresheet_data.ornt_img_low_1_1

        soup.find(id='ornt_img_high_0_0')['src'] = scoresheet_data.ornt_img_high_0_0
        soup.find(id='ornt_img_high_0_1')['src'] = scoresheet_data.ornt_img_high_0_1
        soup.find(id='ornt_img_high_1_0')['src'] = scoresheet_data.ornt_img_high_1_0
        soup.find(id='ornt_img_high_1_1')['src'] = scoresheet_data.ornt_img_high_1_1

        soup.find(id='ornt_img_low_0_0')['title'] = scoresheet_data.ornt_img_low_0_0        
        soup.find(id='ornt_img_low_0_1')['title'] = scoresheet_data.ornt_img_low_0_1
        soup.find(id='ornt_img_low_1_0')['title'] = scoresheet_data.ornt_img_low_1_0
        soup.find(id='ornt_img_low_1_1')['title'] = scoresheet_data.ornt_img_low_1_1

        soup.find(id='ornt_img_high_0_0')['title'] = scoresheet_data.ornt_img_high_0_0
        soup.find(id='ornt_img_high_0_1')['title'] = scoresheet_data.ornt_img_high_0_1
        soup.find(id='ornt_img_high_1_0')['title'] = scoresheet_data.ornt_img_high_1_0
        soup.find(id='ornt_img_high_1_1')['title'] = scoresheet_data.ornt_img_high_1_1

        # image borders -> for easily telling them apart in the 3D visualization.
        soup.find(id='ornt_img_low_0_0')['style'] = style_str_0
        soup.find(id='ornt_img_low_0_1')['style'] = style_str_1
        soup.find(id='ornt_img_low_1_0')['style'] = style_str_0
        soup.find(id='ornt_img_low_1_1')['style'] = style_str_1

        soup.find(id='ornt_img_high_0_0')['style'] = style_str_0
        soup.find(id='ornt_img_high_0_1')['style'] = style_str_1
        soup.find(id='ornt_img_high_1_0')['style'] = style_str_0
        soup.find(id='ornt_img_high_1_1')['style'] = style_str_1

        # 3d visualizations
        soup.find(id='ornt_vis_low_0_0')['src'] = scoresheet_data.ornt_vis_low_0_0
        soup.find(id='ornt_vis_low_0_1')['src'] = scoresheet_data.ornt_vis_low_0_1
        soup.find(id='ornt_vis_low_1_0')['src'] = scoresheet_data.ornt_vis_low_1_0
        soup.find(id='ornt_vis_low_1_1')['src'] = scoresheet_data.ornt_vis_low_1_1

        soup.find(id='ornt_vis_high_0_0')['src'] = scoresheet_data.ornt_vis_high_0_0
        soup.find(id='ornt_vis_high_0_1')['src'] = scoresheet_data.ornt_vis_high_0_1
        soup.find(id='ornt_vis_high_1_0')['src'] = scoresheet_data.ornt_vis_high_1_0
        soup.find(id='ornt_vis_high_1_1')['src'] = scoresheet_data.ornt_vis_high_1_1
        
        # errors
        soup.find(id='ornt_low_0_error0').string.replace_with(str(scoresheet_data.ornt_low_0_error0))
        soup.find(id='ornt_low_0_error1').string.replace_with(str(scoresheet_data.ornt_low_0_error1))
        soup.find(id='ornt_low_1_error0').string.replace_with(str(scoresheet_data.ornt_low_1_error0))
        soup.find(id='ornt_low_1_error1').string.replace_with(str(scoresheet_data.ornt_low_1_error1))
        soup.find(id='ornt_high_0_error0').string.replace_with(str(scoresheet_data.ornt_high_0_error0))
        soup.find(id='ornt_high_0_error1').string.replace_with(str(scoresheet_data.ornt_high_0_error1))
        soup.find(id='ornt_high_1_error0').string.replace_with(str(scoresheet_data.ornt_high_1_error0))
        soup.find(id='ornt_high_1_error1').string.replace_with(str(scoresheet_data.ornt_high_1_error1))

        # soup.find(id='position_score').string.replace_with(scoresheet_data.position_score)

        # soup.find(id='pos_img_low_0_0')['src'] = scoresheet_data.pos_img_low_0_0
        # soup.find(id='pos_img_low_0_1')['src'] = scoresheet_data.pos_img_low_0_1
        # soup.find(id='pos_img_low_1_0')['src'] = scoresheet_data.pos_img_low_1_0
        # soup.find(id='pos_img_low_1_1')['src'] = scoresheet_data.pos_img_low_1_1
        # soup.find(id='pos_img_low_2_0')['src'] = scoresheet_data.pos_img_low_2_0
        # soup.find(id='pos_img_low_2_1')['src'] = scoresheet_data.pos_img_low_2_1

        # soup.find(id='pos_img_high_0_0')['src'] = scoresheet_data.pos_img_high_0_0
        # soup.find(id='pos_img_high_0_1')['src'] = scoresheet_data.pos_img_high_0_1
        # soup.find(id='pos_img_high_1_0')['src'] = scoresheet_data.pos_img_high_1_0
        # soup.find(id='pos_img_high_1_1')['src'] = scoresheet_data.pos_img_high_1_1
        # soup.find(id='pos_img_high_2_0')['src'] = scoresheet_data.pos_img_high_2_0
        # soup.find(id='pos_img_high_2_1')['src'] = scoresheet_data.pos_img_high_2_1

        # Store prettified version of modified html
        new_text = soup.prettify()

    # Write new contents to test.html
    with open(f'{output_folder}/compare-sheet.html', mode='w') as new_html_file:
        new_html_file.write(new_text)

    print(f"Written compare-sheet file to: {output_folder}/compare-sheet.html")