from bs4 import BeautifulSoup
from collections import namedtuple

fields = ['orientation_score',
        'ornt_img_low_0_0', 'ornt_img_low_0_1',
        'ornt_vis_low_0_ext', 'ornt_vis_low_0_ref',
        'ornt_low_0_error',
        'ornt_img_low_1_0', 'ornt_img_low_1_1',
        'ornt_vis_low_1_ext', 'ornt_vis_low_1_ref',
        'ornt_low_1_error',
        'ornt_img_low_2_0', 'ornt_img_low_2_1',
        'ornt_vis_low_2_ext', 'ornt_vis_low_2_ref',
        'ornt_low_2_error',
        'ornt_img_high_0_0', 'ornt_img_high_0_1',
        'ornt_vis_high_0_ext', 'ornt_vis_high_0_ref',
        'ornt_high_0_error',
        'ornt_img_high_1_0', 'ornt_img_high_1_1',
        'ornt_vis_high_1_ext', 'ornt_vis_high_1_ref',
        'ornt_high_1_error',
        'ornt_img_high_2_0', 'ornt_img_high_2_1',
        'ornt_vis_high_2_ext', 'ornt_vis_high_2_ref',
        'ornt_high_2_error',
        'position_score',                                                
        'pos_img_low_0_0', 'pos_img_low_0_1',
        'pos_img_low_1_0', 'pos_img_low_1_1',
        'pos_img_low_2_0', 'pos_img_low_2_1',
        'pos_img_high_0_0', 'pos_img_high_0_1',
        'pos_img_high_1_0', 'pos_img_high_1_1',
        'pos_img_high_2_0', 'pos_img_high_2_1',
        'image_color_0', 'image_color_1']

ScoresheetData = namedtuple('ScoresheetData', fields, defaults=(None,) * len(fields))

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