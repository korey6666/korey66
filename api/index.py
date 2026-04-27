"""
Vercel Serverless Flask Application for House Price Prediction
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
import pandas as pd
import numpy as np
import pickle
import json
import os

app = Flask(__name__, template_folder='../web/templates')

# 设置路径 - Vercel环境下使用绝对路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS_DIR = os.path.join(BASE_DIR, 'models')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

# 全局变量用于缓存加载的数据
_model = None
_model_info = None
_label_encoder = None
_predictions_df = None
_feature_importance_df = None
_test_report = None

def load_model_data():
    """懒加载模型和数据"""
    global _model, _model_info, _label_encoder, _predictions_df, _feature_importance_df, _test_report
    
    if _model is None:
        try:
            with open(os.path.join(MODELS_DIR, 'decision_tree_model.pkl'), 'rb') as f:
                _model = pickle.load(f)
        except Exception as e:
            print(f"Error loading model: {e}")
            _model = None
    
    if _model_info is None:
        try:
            with open(os.path.join(MODELS_DIR, 'model_info.json'), 'r') as f:
                _model_info = json.load(f)
        except Exception as e:
            print(f"Error loading model info: {e}")
            _model_info = None
    
    if _label_encoder is None:
        try:
            with open(os.path.join(MODELS_DIR, 'label_encoder.pkl'), 'rb') as f:
                _label_encoder = pickle.load(f)
        except Exception as e:
            print(f"Error loading label encoder: {e}")
            _label_encoder = None
    
    if _predictions_df is None:
        try:
            _predictions_df = pd.read_csv(os.path.join(OUTPUTS_DIR, 'model', 'test_predictions.csv'))
        except Exception as e:
            print(f"Error loading predictions: {e}")
            _predictions_df = None
    
    if _feature_importance_df is None:
        try:
            _feature_importance_df = pd.read_csv(os.path.join(OUTPUTS_DIR, 'test_analysis', 'feature_importance.csv'))
        except Exception as e:
            print(f"Error loading feature importance: {e}")
            _feature_importance_df = None
    
    if _test_report is None:
        try:
            with open(os.path.join(OUTPUTS_DIR, 'test_analysis', 'test_report.json'), 'r') as f:
                _test_report = json.load(f)
        except Exception as e:
            print(f"Error loading test report: {e}")
            _test_report = None

@app.route('/')
def index():
    """首页"""
    return render_template('index.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    """预测页面"""
    load_model_data()
    
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
            data['ocean_proximity_encoded'] = int(_label_encoder.transform([data['ocean_proximity']])[0])
            
            # 准备特征向量
            features = _model_info['features']
            input_data = np.array([[data[f] for f in features]])
            
            # 预测
            prediction = _model.predict(input_data)[0]
            
            return jsonify({
                'success': True,
                'predicted_price': round(float(prediction), 2),
                'input_data': data
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # GET请求返回预测页面
    ocean_categories = list(_label_encoder.classes_) if _label_encoder else ['<1H OCEAN', 'INLAND', 'ISLAND', 'NEAR BAY', 'NEAR OCEAN']
    return render_template('predict.html', ocean_categories=ocean_categories)

@app.route('/results')
def results():
    """测试结果页面"""
    load_model_data()
    
    if _predictions_df is not None:
        # 准备图表数据
        sample_data = _predictions_df.head(100).to_dict('records')
        
        # 统计信息
        stats = {
            'total_samples': len(_predictions_df),
            'mean_error': round(_predictions_df['residual'].abs().mean(), 2),
            'rmse': round(np.sqrt((_predictions_df['residual'] ** 2).mean()), 2),
            'r2': round(_test_report['metrics']['test']['r2'], 4) if _test_report else 'N/A'
        }
        
        return render_template('results.html', 
                             sample_data=sample_data,
                             stats=stats,
                             feature_importance=_feature_importance_df.head(10).to_dict('records') if _feature_importance_df is not None else [])
    return render_template('results.html', sample_data=[], stats={}, feature_importance=[])

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """API接口用于预测"""
    load_model_data()
    
    try:
        data = request.get_json()
        
        # 特征工程
        data['rooms_per_person'] = data['total_rooms'] / data['population']
        data['rooms_per_household'] = data['total_rooms'] / data['households']
        data['bedrooms_per_household'] = data['total_bedrooms'] / data['households']
        data['bedroom_ratio'] = data['total_bedrooms'] / data['total_rooms']
        data['population_per_household'] = data['population'] / data['households']
        data['income_per_room'] = data['median_income'] / data['total_rooms']
        data['ocean_proximity_encoded'] = int(_label_encoder.transform([data['ocean_proximity']])[0])
        
        # 准备特征向量
        features = _model_info['features']
        input_data = np.array([[data[f] for f in features]])
        
        # 预测
        prediction = _model.predict(input_data)[0]
        
        return jsonify({
            'success': True,
            'predicted_price': round(float(prediction), 2)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/stats')
def api_stats():
    """API接口获取统计信息"""
    load_model_data()
    
    if _test_report:
        return jsonify(_test_report)
    return jsonify({'error': 'No test report available'}), 404
