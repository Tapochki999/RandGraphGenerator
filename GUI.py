import networkx as nx
import FreeSimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from GraphLogic import Graph
import datetime
import sys
import os
import json
import time

P = Graph()

treedata = sg.TreeData()
win_height = 1000
win_width = 700
WORK_DIR = None

def load_history_from_json(folder):
    json_path = os.path.join(folder, 'history.json')
    data = []
    if os.path.exists(json_path):
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = []
    return data

def save_history_to_json(folder, history_data):
    json_path = os.path.join(folder, 'history.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=4)
    except:
        pass

def refresh_tree_data(history_data):
    new_tree = sg.TreeData()
    for item in history_data:
        new_tree.Insert('', key=item['id'], text=item['name'], values=[item['date'], item['weight']])
    return new_tree

main_col1 = [
    [sg.Text('Робоча папка не вибрана', key='-DIR_STATUS-', size=(30, 1), text_color='orange')],
    [sg.Button('Обрати робочу папку')],
    [sg.HorizontalSeparator()],
    [sg.Button('Створити новий граф')],
    [sg.Button('Відкрити граф')],
    [sg.Button("Видалити граф")],
    [sg.Button("Очистити всю історію графів")],
    [sg.Button("Про програму")],
    [sg.Button("Вихід")]]
main_col2 = [
    [sg.Push(), sg.Tree(treedata, headings=('Дата створення', 'Вага (Bytes)'), row_height=20, num_rows=20, col0_width=30, key='-TREE-', expand_x=True, expand_y=True)]]

layout_main = sg.Column([
    [sg.Column(main_col1, size=(win_width*0.3, win_height), pad=(0,0), element_justification='l', vertical_alignment='top'), sg.VerticalSeparator(), sg.Column(main_col2, pad=(0,0), expand_x=True, expand_y=True)]
], key='-LAYOUT_MAIN-', expand_x=True, expand_y=True)

Menu_layout = [['Зберегти', ['Зберегти граф (.txt)', 'Зберегти всі мережеві параметри (.csv)', 'Зберегти всі мережеві параметри (.xsl)']]] 

weight_layout = [ 
    [sg.Text('Введіть інтервал', key='TEXT4')], 
    [sg.Text('Від', key='TEXT5'), sg.Input(key='-FROM-', size=(5, None)), sg.Text('До', key='TEXT6'), sg.Input(key='-TO-', size=(5, None))]
]

erdos_layout = [
    [sg.Text('Ймовірність', key='TEXT2'), sg.Input(key='-P-', tooltip='Від 0 до 100', size=(3, None)), sg.Text('%', key='%')]
]

config_layout = [
    [sg.Text("Кількість сусідів:", key='TEXT3'),  sg.Input(key='-NEIGHBOURS-', size=(5, None))]
]

barabasi_layout = [
    [sg.Text("Кількість нових ребер (m):", key='TEXT_BA'), sg.Input(key='-BA_M-', size=(5, None))]
]

watts_layout = [
    [sg.Text("Сусіди (k):", key='TEXT_WS_K'), sg.Input(key='-WS_K-', size=(5, None))],
    [sg.Text("Ймовірність:", key='TEXT_WS_P'), sg.Input(key='-WS_P-', size=(3, None)), sg.Text('%')]
]

graph_col1 = [
    [sg.Button('Назад')],
    [sg.Text('Тип'), sg.Combo(['Ердоша-Реньї', 'Конфігураційна модель', 'Барабаші-Альберта', 'Тісного світу'], size=(20,None), default_value='Ердоша-Реньї', key='-TYPE-', enable_events=True), sg.Push()],
    [sg.Text('Кількість вершин', key='TEXT1'), sg.Input(key='-NODES-', size=(5, None) ,  tooltip='1, 2, 15, тощо'), sg.Push()],
    [sg.pin(sg.Column(erdos_layout, key='-ERDOS_PANEL-', visible=True, pad=(0,0)))],
    [sg.pin(sg.Column(config_layout, key='-CONFIG_PANEL-', visible=False, pad=(0,0)))],
    [sg.pin(sg.Column(barabasi_layout, key='-BARABASI_PANEL-', visible=False, pad=(0,0)))],
    [sg.pin(sg.Column(watts_layout, key='-WATTS_PANEL-', visible=False, pad=(0,0)))],
    [sg.Checkbox("Орієнтованість графа", key="-DERICTED-")],
    [sg.Checkbox("Вага ребер", key="-WEIGHT-", enable_events=True)], 
    [sg.pin(sg.Column(weight_layout, key='-WEIGHT_PANEL-', visible=False, pad=(0,0)))],
    [sg.Button("Показати метрики")], 
    [sg.Button('Створити'), sg.Push()]]
graph_col2 = [
    [sg.Canvas(key='-CONTROLS-')],
    [sg.Canvas(key='-CANVAS-', expand_x=True, expand_y=True)]]

layout_graph = sg.Column([
    [sg.Column(graph_col1, size=(win_width*0.3, win_height), pad=(0,0), element_justification='l'), sg.VerticalSeparator(), sg.Column(graph_col2, pad=(0,0), expand_x=True, expand_y=True)]
], key='-LAYOUT_GRAPH-', visible=False, expand_x=True, expand_y=True)

layout = [
    [sg.Menu(Menu_layout)],
    [layout_main, layout_graph]
]

window = sg.Window('Програма для генерації графів', layout ,size=(win_height, win_width), finalize=True)

try:
    default_folder = "Saved Data"
    current_dir = os.getcwd()
    auto_path = os.path.join(current_dir, default_folder)
    os.makedirs(auto_path, exist_ok=True)
    WORK_DIR = auto_path
    window['-DIR_STATUS-'].update(f'Папка: {default_folder}', text_color='green')
    history = load_history_from_json(WORK_DIR)
    treedata = refresh_tree_data(history)
    window['-TREE-'].update(treedata)
except Exception as e:
    sg.popup_error(f"Не вдалося створити автоматичну папку: {e}")

def draw_figure_w_toolbar(canvas, toolbar_canvas, figure):
    if canvas.children:
        for child in canvas.winfo_children():
            child.destroy()
    if toolbar_canvas.children:
        for child in toolbar_canvas.winfo_children():
            child.destroy()

    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)

    toolbar = NavigationToolbar2Tk(figure_canvas_agg, toolbar_canvas)
    toolbar.update()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    
    return figure_canvas_agg

while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, 'Вихід'):
        break
    
    if event == 'Обрати робочу папку':
        folder = sg.popup_get_folder('Оберіть папку для зберігання історії графів')
        if folder:
            WORK_DIR = folder
            window['-DIR_STATUS-'].update(f'Папка: {os.path.basename(folder)}', text_color='green')
            
            history = load_history_from_json(WORK_DIR)
            treedata = refresh_tree_data(history)
            window['-TREE-'].update(treedata)

    if event == '-WEIGHT-':
        window['-WEIGHT_PANEL-'].update(visible=values['-WEIGHT-'])

    if event == '-TYPE-':       
        is_erdos = (values['-TYPE-'] == 'Ердоша-Реньї')
        is_config = (values['-TYPE-'] == 'Конфігураційна модель')
        is_barabasi = (values['-TYPE-'] == 'Барабаші-Альберта')
        is_watts = (values['-TYPE-'] == 'Тісного світу')
        
        window['-ERDOS_PANEL-'].update(visible=is_erdos)
        window['-CONFIG_PANEL-'].update(visible=is_config)
        window['-BARABASI_PANEL-'].update(visible=is_barabasi)
        window['-WATTS_PANEL-'].update(visible=is_watts)
    
    if event == 'Показати метрики':
        if P.G is None:
             sg.popup_error("Граф ще не створено або не завантажено.")
        else:
             if not P.metrics:
                 P.calculate_metrics()
             
             res_text = f'ACC: {P.metrics.get("ACC", 0)}\n'
             res_text += f'ANC: {P.metrics.get("ANC", 0)}\n'
             res_text += f'APL: {P.metrics.get("APL", 0)}'
             sg.popup(res_text, title='Результати')

    if event == 'Про програму':
        sg.popup("Програма Random graph generator\n"
        "Навчальна програма для створення випадкових графів\n"
        "Версія: 1.0.0\n" 
        "Ліцензія: Free for educational use\n"
        "Навчальний заклад: ЛНУ імені Івана Франка\n"
        "Кафедра оптоелектроніки та інформаційних технологій\n"
        "Курсова робота\n"
        "Керівник: Кушнір Олег Степанович\n" 
        "Автор: Гусяк Володимир Михайлович\n"
        "Львів 2025", background_color="Green", no_titlebar=True)

    if event == 'Створити':
        if not WORK_DIR:
            sg.popup_error("Спочатку оберіть робочу папку!", title="Помилка")
            continue

        try:
            nodes_str = values['-NODES-']
            if not nodes_str.strip():
                sg.popup_error("Будь ласка, введіть кількість вершин.")
                continue
            
            try:
                nodes = int(nodes_str)
            except ValueError:
                 sg.popup_error("Кількість вершин повинна бути цілим числом.")
                 continue

            if nodes <= 0:
                sg.popup_error("Кількість вершин повинна бути додатною.")
                continue

            current_type = values['-TYPE-']
            p_val = 0
            neighbours = 0

            if current_type == 'Ердоша-Реньї':
                p_str = values['-P-']
                if not p_str.strip():
                    sg.popup_error("Будь ласка, введіть ймовірність.")
                    continue
                try:
                    p_val = int(p_str)
                except ValueError:
                    sg.popup_error("Ймовірність повинна бути цілим числом.")
                    continue
                
                if p_val < 0 or p_val > 100:
                    sg.popup_error("Ймовірність повинна бути від 0 до 100.")
                    continue

            elif current_type == 'Конфігураційна модель':
                neighbours_str = values['-NEIGHBOURS-']
                if not neighbours_str.strip():
                     sg.popup_error("Будь ласка, введіть кількість сусідів.")
                     continue
                try:
                    neighbours = int(neighbours_str)
                except ValueError:
                    sg.popup_error("Кількість сусідів повинна бути цілим числом.")
                    continue

                if neighbours < 0:
                    sg.popup_error("Кількість сусідів не може бути від'ємною.")
                    continue
                
                if neighbours >= nodes:
                    sg.popup_error(f"Кількість сусідів ({neighbours}) повинна бути меншою за кількість вузлів ({nodes})!")
                    continue
            
            elif current_type == 'Барабаші-Альберта':
                neighbours_str = values['-BA_M-']
                if not neighbours_str.strip():
                     sg.popup_error("Будь ласка, введіть кількість нових ребер (m).")
                     continue
                try:
                    neighbours = int(neighbours_str)
                except ValueError:
                    sg.popup_error("Кількість ребер (m) повинна бути цілим числом.")
                    continue

                if neighbours < 1:
                    sg.popup_error("Кількість ребер (m) повинна бути не менше 1.")
                    continue
                
                if neighbours >= nodes:
                    sg.popup_error(f"Кількість ребер ({neighbours}) повинна бути меншою за кількість вузлів ({nodes})!")
                    continue

            elif current_type == 'Тісного світу':
                k_str = values['-WS_K-']
                p_str = values['-WS_P-']
                
                if not k_str.strip() or not p_str.strip():
                     sg.popup_error("Будь ласка, заповніть всі поля.")
                     continue
                
                try:
                    neighbours = int(k_str)
                    p_val = int(p_str)
                except ValueError:
                    sg.popup_error("Значення повинні бути числами.")
                    continue
                
                if neighbours >= nodes:
                    sg.popup_error(f"Кількість сусідів ({neighbours}) повинна бути меншою за кількість вузлів ({nodes})!")
                    continue
                    
                if p_val < 0 or p_val > 100:
                    sg.popup_error("Ймовірність повинна бути від 0 до 100.")
                    continue
            
            is_directed = values['-DERICTED-']
            is_weighted = values['-WEIGHT-']
            w_from = 0
            w_to = 0
            
            if is_weighted:
                wf_str = values['-FROM-']
                wt_str = values['-TO-']
                
                if not wf_str.strip() or not wt_str.strip():
                    sg.popup_error("Будь ласка, введіть інтервал ваги.")
                    continue
                    
                try:
                    w_from = int(wf_str)
                    w_to = int(wt_str)
                    
                    if w_from < 0 or w_to < 0:
                         sg.popup_error("Значення меж інтервалу повинно бути додатнім.")
                         continue
                         
                    if w_from > w_to:
                         sg.popup_error("Початкове значення ваги має бути меншим або рівним кінцевому.")
                         continue
                except ValueError:
                    sg.popup_error("Значення ваги мають бути цілими числами.")
                    continue

            window.perform_long_operation(lambda: None, '-DUMMY-')
            
            is_created = P.create(current_type, nodes, p_val, neighbours, is_directed, is_weighted, w_from, w_to)
            
            if is_created:
                P.calculate_metrics()
                
                creation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                timestamp_id = str(int(time.time()))
                try:
                    graph_weight = sys.getsizeof(P.G)
                except:
                    graph_weight = 0
                
                file_name = f"graph_{timestamp_id}.txt"
                full_path = os.path.join(WORK_DIR, file_name)
                P.save_graph(full_path)
                
                metrics_name = f"metrics_{timestamp_id}.csv"
                metrics_path = os.path.join(WORK_DIR, metrics_name)
                P.save_all_metrics(metrics_path)

                history = load_history_from_json(WORK_DIR)
                new_record = {
                    'id': timestamp_id,
                    'name': f"{current_type} (N={nodes})",
                    'date': creation_date,
                    'weight': graph_weight,
                    'file': file_name,
                    'metrics_file': metrics_name,
                    'is_directed': is_directed,
                    'is_weighted': is_weighted
                }
                history.append(new_record)
                save_history_to_json(WORK_DIR, history)

                treedata = refresh_tree_data(history)
                window['-TREE-'].update(treedata)

                res_text = f'Час генерації: {P.last_time} с\n'
                res_text += f'ACC: {P.metrics.get("ACC", 0)}\n'
                res_text += f'ANC: {P.metrics.get("ANC", 0)}\n'
                res_text += f'APL: {P.metrics.get("APL", 0)}'
                sg.popup(res_text, title='Результати')
                
                fig = P.get_figure()
                draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, window['-CONTROLS-'].TKCanvas, fig)
            else:
                sg.popup_error('Помилка при створенні графу. Перевірте параметри.')
                
        except Exception as e:
            sg.popup_error(f"Критична помилка: {e}")

    if event == 'Відкрити граф':
        if not WORK_DIR:
             sg.popup_error("Спочатку оберіть робочу папку!", title="Помилка")
             continue
             
        selected = values['-TREE-']
        if selected:
            selected_id = selected[0]
            history = load_history_from_json(WORK_DIR)
            record = next((item for item in history if item['id'] == selected_id), None)
            
            if record:
                file_path = os.path.join(WORK_DIR, record['file'])
                if os.path.exists(file_path):
                    is_directed = record.get('is_directed', False)
                    is_weighted = record.get('is_weighted', False)

                    if P.load_graph(file_path, is_directed, is_weighted):
                        P.calculate_metrics()
                        
                        window['-LAYOUT_MAIN-'].update(visible=False)
                        window['-LAYOUT_GRAPH-'].update(visible=True)
                        
                        fig = P.get_figure()
                        draw_figure_w_toolbar(window['-CANVAS-'].TKCanvas, window['-CONTROLS-'].TKCanvas, fig)
                        
                        metrics_text = f"Граф завантажено: {record['name']}\n"
                        metrics_text += f'ACC: {P.metrics.get("ACC", 0)}\n'
                        metrics_text += f'ANC: {P.metrics.get("ANC", 0)}\n'
                        metrics_text += f'APL: {P.metrics.get("APL", 0)}'
                        sg.popup(metrics_text, title="Інформація")
                    else:
                        sg.popup_error("Не вдалося прочитати файл графу.")
                else:
                    sg.popup_error("Файл графу не знайдено.")
        else:
            sg.popup("Виберіть граф зі списку")

    if event == 'Видалити граф':
        if not WORK_DIR:
             sg.popup_error("Спочатку оберіть робочу папку!", title="Помилка")
             continue
        
        selected = values['-TREE-']
        if selected:
            if sg.popup_yes_no('Ви впевнені, що хочете видалити цей граф?') == 'Yes':
                selected_id = selected[0]
                history = load_history_from_json(WORK_DIR)
                
                record = next((item for item in history if item['id'] == selected_id), None)
                if record:
                    try:
                        file_path = os.path.join(WORK_DIR, record['file'])
                        metrics_path = os.path.join(WORK_DIR, record['metrics_file'])
                        
                        if os.path.exists(file_path):
                            os.remove(file_path)
                        if os.path.exists(metrics_path):
                            os.remove(metrics_path)
                    except Exception as e:
                        print(f"Помилка при видаленні файлів: {e}")

                    history = [item for item in history if item['id'] != selected_id]
                    save_history_to_json(WORK_DIR, history)
                    
                    treedata = refresh_tree_data(history)
                    window['-TREE-'].update(treedata)
        else:
            sg.popup("Будь ласка, оберіть граф для видалення.")

    if event == 'Очистити всю історію графів':
        if not WORK_DIR:
             sg.popup_error("Спочатку оберіть робочу папку!", title="Помилка")
             continue
        
        if sg.popup_yes_no('Ви впевнені, що хочете видалити всю історію та файли графів?') == 'Yes':
            history = load_history_from_json(WORK_DIR)
            
            for item in history:
                try:
                    file_path = os.path.join(WORK_DIR, item['file'])
                    metrics_path = os.path.join(WORK_DIR, item['metrics_file'])
                    
                    if os.path.exists(file_path):
                        os.remove(file_path)
                    if os.path.exists(metrics_path):
                        os.remove(metrics_path)
                except:
                    pass
            
            history = []
            save_history_to_json(WORK_DIR, history)
            
            treedata = refresh_tree_data(history)
            window['-TREE-'].update(treedata)

    if event == 'Зберегти граф (.txt)':
        path = sg.popup_get_file('Зберегти граф (.txt)', save_as=True, file_types=(("Text Files", "*.txt"),), default_extension='.txt')
        if path:
            P.save_graph(path)

    if event == 'Зберегти всі метрики (.csv)':
        path = sg.popup_get_file('Зберегти метрики', save_as=True, file_types=(("CSV Files", "*.csv"),), default_extension='.csv')
        if path:
            if P.save_all_metrics(path):
                sg.popup('Метрики успішно збережено!')
            else:
                sg.popup_error('Помилка при збереженні метрик або метрики не розраховані.')

    if event == 'Створити новий граф':
        if not WORK_DIR:
             sg.popup_error("Спочатку оберіть робочу папку!", title="Помилка")
             continue
        window['-LAYOUT_MAIN-'].update(visible=False)
        window['-LAYOUT_GRAPH-'].update(visible=True)
        
    if event == 'Назад':
        window['-LAYOUT_GRAPH-'].update(visible=False)
        window['-LAYOUT_MAIN-'].update(visible=True)

window.close()
