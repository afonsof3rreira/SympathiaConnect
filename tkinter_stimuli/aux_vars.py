import os
"""
Tests:
    - T0: Presentation
    - T1: Body movement tests (motion artifacts)
    - T2: Stroop tests (cognitive overload)
    - T3: Maths tests (cognitive overload)
    - T4: Hand-grip tests.

"""

T0_texts = {
    'screen 1': {
        'title': {
            'en': 'Subject section. Please fill in the requested info.',
            'pt': 'Secção do participante. Por favor preencha a informação pedida.'

        },
        'subtitle 1':{
            'en': 'Subject ID (as provided by the research assistant)',
            'pt': 'ID do sujeito (providenciado pelo investigador auxiliar)'
        },
    },
    'screen 2': {
        'title': {
            'en': 'Anthropometric information',
            'pt': 'Informação antropométrica'
        },
        'subtitle 1': {
            'en': 'Age group (years old)',
            'pt': 'Faixa etária (idade)'
        },
        'options 1':
        {
            'en': ['18-29', '30-39', '40-49', '50-59', '60-69', '70-79', '>80'],
            'pt': ['18-29', '30-39', '40-49', '50-59', '60-69', '70-79', '>80'],
        },
        'subtitle 2': {
            'en': 'Sex',
            'pt': 'Sexo'
        },
        'options 2': {
            'en': ['Male', 'Female', 'Other', 'Prefer not to say'],
            'pt': ['Masculino', 'Feminino', 'Outro', 'Prefiro não dizer'],
        },
        'subtitle 3': {
            'en': 'Height',
            'pt': 'Altura'
        },
        'options 3': {
            'en': ['Centimeters (Cm)', 'Inches (")'],
            'pt': ['Centímetros (Cm)', 'Polegadas (")'],
        },
        'subtitle 4': {
            'en': 'Weight',
            'pt': 'Peso'
        },
        'options 4': {
            'en': ['Kilogram (kg)', 'Pound (lb)'],
            'pt': ['Quilograma (kg)', 'Libra (lb)'],
        },
        'subtitle 5': {
            'en': 'Foot / Shoe size',
            'pt': 'Tamanho do pé / sapato'
        },
        'options 5': {
            'en': ['EU', 'UK', 'US'],
            'pt': ['EU', 'UK', 'US'],
        }
    },
    'screen 3': {
        'title': {
            'en': 'Anthropometric information',
            'pt': 'Informação antropométrica'
        },
        'subtitle 1': {
            'en': 'Ankle perimeter (measured in centimeters)',
            'pt': 'Perímetro do tornozelo (medido em centímetros)'
        },
    }
}

T1_action_texts = {
            "original": 'Press Space to perform movement',
            0: ["lifting left arm", "Lowering left arm", "back to original position"],
            1: ["lifting left leg", "Lowering left leg", "back to original position"],
            2: ["lifting right arm", "Lowering right arm", "back to original position"],
            3: ["lifting right leg", "Lowering right leg", "back to original position"],
        }

T1_image_paths = {
            "original": os.path.join(os.path.dirname(__file__), "images", "body.jpeg"),
            0: os.path.join(os.path.dirname(__file__), "images", "body_task_1.jpg"),
            1: os.path.join(os.path.dirname(__file__), "images", "body_task_2.jpg"),
            2: os.path.join(os.path.dirname(__file__), "images", "body_task_3.jpg"),
            3: os.path.join(os.path.dirname(__file__), "images", "body_task_4.jpg"),
        }

T2_colors_PT = [
    ["Vermelho", "#FF0000"],
    ["Verde", "#008000"],
    ["Azul", "#0000FF"],
    ["Amarelo", "#FFFF00"],
    ["Roxo", "#800080"],
    ["Laranja", "#FFA500"],
    ["Rosa", "#FFC0CB"],
    ["Castanho", "#A52A2A"],
    ["Preto", "#000000"],
    ["Branco", "#FFFFFF"]
]


T2_colors_EN = [
    ["Red", "#FF0000"],
    ["Green", "#008000"],
    ["Blue", "#0000FF"],
    ["Yellow", "#FFFF00"],
    ["Purple", "#800080"],
    ["Orange", "#FFA500"],
    ["Pink", "#FFC0CB"],
    ["Brown", "#A52A2A"],
    ["Black", "#000000"],
    ["White", "#FFFFFF"]
]

