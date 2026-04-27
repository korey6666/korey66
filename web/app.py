"""
Flask Web Application for House Price Prediction
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
import pickle
import json
import os

app = Flask(__name__)

# 设置路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

# 加载模型和相关信息
with open(os.path.join(MODELS_DIR, 'decision_tree_model.pkl'), 'rb') as f:
    model = pickle.load(f)

with open(os.path.join(MODELS_DIR, 'model_info.json'), 'r') as f:
    model_info = json.load(f)

with open(os.path.join(MODELS_DIR, 'label_encoder.pkl'), 'rb') as f:
    label_encoder = pickle.load(f)

# 加载测试数据用于展示
try:
    predictions_df = pd.read_csv(os.path.join(OUTPUTS_DIR, 'model', 'test_predictions.csv'))
    feature_importance_df = pd.read_csv(os.path.join(OUTPUTS_DIR, 'test_analysis', 'feature_importance.csv'))
    with open(os.path.join(OUTPUTS_DIR, 'test_analysis', 'test_report.json'), 'r') as f:
        test_report = json.load(f)
except Exception as e:
    print(f"Error loading test data: {e}")
    predictions_df = None
    feature_importance_df = None
    test_report = None

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """预测页面"""
    if request.method == 'POST':
        try:
            # 获取表单数据
            data = {
                'longitude': float(request.form['longitude']),
                'latitude': float(request.form['latitude']),
                'housing_median_age': float(request.form['housing_median_age']),
                'total_rooms': float(request.form['total_rooms']),
                'total_bedrooms': float(request.form['total_bedrooms']),
                'population': float(request.form['population']),
                'households': float(request.form['households']),
                'median_income': float(request.form['median_income']),
                'ocean_proximity': request.form['ocean_proximity']
            }
            
            # 特征工程
            data['rooms_per_person'] = data['total_rooms'] / data['population']
            data['rooms_per_household'] = data['total_rooms'] / data['households']
            data['bedrooms_per_household'] = data['total_bedrooms'] / data['households']
            data['bedroom_ratio'] = data['total_bedrooms'] / data['total_rooms']
            data['population_per_household'] = data['population'] / data['households']
            data['income_per_room'] = data['median_income'] / data['total_rooms']
            
            # 编码分类变量
            data['ocean_proximity_encoded'] = int(label_encoder.transform([data['ocean_proximity']])[0])
            
            # 准备特征向量
            features = model_info['features']
            input_data = np.array([[data[f] for f in features]])
            
            # 预测
            prediction = model.predict(input_data)[0]
            
            return jsonify({
                'success': True,
                'predicted_price': round(float(prediction), 2),
                'input_data': data
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # GET请求返回预测页面
    ocean_categories = list(label_encoder.classes_)
    return render_template('predict.html', ocean_categories=ocean_categories)

@app.route('/results')
def results():
    """测试结果页面"""
    if predictions_df is not None:
        # 准备图表数据
        sample_data = predictions_df.head(100).to_dict('records')
        
        # 统计信息
        stats = {
            'total_samples': len(predictions_df),
            'mean_error': round(predictions_df['residual'].abs().mean(), 2),
            'rmse': round(np.sqrt((predictions_df['residual'] ** 2).mean()), 2),
            'r2': round(test_report['metrics']['test']['r2'], 4) if test_report else 'N/A'
        }
        
        return render_template('results.html', 
                             sample_data=sample_data,
                             stats=stats,
                             feature_importance=feature_importance_df.head(10).to_dict('records') if feature_importance_df is not None else [])
    return render_template('results.html', sample_data=[], stats={}, feature_importance=[])

@app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件"""
    return send_from_directory(os.path.join(OUTPUTS_DIR, 'test_analysis'), filename)

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API接口用于预测"""
    try:
        data = request.get_json()
        
        # 特征工程
        data['rooms_per_person'] = data['total_rooms'] / data['population']
        data['rooms_per_household'] = data['total_rooms'] / data['households']
        data['bedrooms_per_household'] = data['total_bedrooms'] / data['households']
        data['bedroom_ratio'] = data['total_bedrooms'] / data['total_rooms']
        data['population_per_household'] = data['population'] / data['households']
        data['income_per_room'] = data['median_income'] / data['total_rooms']
        data['ocean_proximity_encoded'] = int(label_encoder.transform([data['ocean_proximity']])[0])
        
        # 准备特征向量
        features = model_info['features']
        input_data = np.array([[data[f] for f in features]])
        
        # 预测
        prediction = model.predict(input_data)[0]
        
        return jsonify({
            'success': True,
            'predicted_price': round(float(prediction), 2)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stats')
def api_stats():
    """API接口获取统计信息"""
    if test_report:
        return jsonify(test_report)
    return jsonify({'error': 'No test report available'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
