from bs4 import BeautifulSoup
from collections import namedtuple

fields = ['orientation_score',
        'ornt_img_low_0_0', 'ornt_img_low_0_1',
        'ornt_img_low_1_0', 'ornt_img_low_1_1',
        'ornt_img_low_2_0', 'ornt_img_low_2_1',
        'ornt_img_high_0_0', 'ornt_img_high_0_1',
        'ornt_img_high_1_0', 'ornt_img_high_1_1',
        'ornt_img_high_2_0', 'ornt_img_high_2_1',
        'position_score',                                                
        'pos_img_low_0_0', 'pos_img_low_0_1',
        'pos_img_low_1_0', 'pos_img_low_1_1',
        'pos_img_low_2_0', 'pos_img_low_2_1',
        'pos_img_high_0_0', 'pos_img_high_0_1',
        'pos_img_high_1_0', 'pos_img_high_1_1',
        'pos_img_high_2_0', 'pos_img_high_2_1']

ScoresheetData = namedtuple('ScoresheetData', fields, defaults=(None,) * len(fields))

def create_scoresheet(scoresheet_data, output_folder):

    with open('scoresheet-template.html') as html_file:
        soup = BeautifulSoup(html_file.read(), features='html.parser')

        soup.find(id='orientation_score').string.replace_with(str(scoresheet_data.orientation_score))

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