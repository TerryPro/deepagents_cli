"""线性回归示例
使用 scikit-learn 实现简单的线性回归
"""

import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

# 设置随机种子以确保可重复性
np.random.seed(42)

# 1. 生成模拟数据
# 创建特征 X：100个样本，1个特征
n_samples = 100
X = 2 * np.random.rand(n_samples, 1)  # 在[0, 2)范围内均匀分布

# 创建目标值 y：y = 3*X + 4 + 噪声
true_slope = 3
true_intercept = 4
noise = np.random.randn(n_samples, 1) * 0.5  # 高斯噪声
y = true_slope * X + true_intercept + noise

print("数据生成完成")
print(f"样本数量: {n_samples}")
print(f"真实斜率: {true_slope}")
print(f"真实截距: {true_intercept}")

# 2. 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\n训练集大小: {X_train.shape[0]}")
print(f"测试集大小: {X_test.shape[0]}")

# 3. 创建和训练线性回归模型
model = LinearRegression()
model.fit(X_train, y_train)

# 4. 获取模型参数
print("\n模型参数:")
print(f"学习到的斜率: {model.coef_[0][0]:.4f}")
print(f"学习到的截距: {model.intercept_[0]:.4f}")
print(f"真实斜率: {true_slope}")
print(f"真实截距: {true_intercept}")

# 5. 在测试集上进行预测
y_pred = model.predict(X_test)

# 6. 评估模型性能
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("\n模型评估:")
print(f"均方误差 (MSE): {mse:.4f}")
print(f"R² 分数: {r2:.4f}")

# 7. 可视化结果
plt.figure(figsize=(12, 5))

# 子图1：训练数据和回归线
plt.subplot(1, 2, 1)
plt.scatter(X_train, y_train, color="blue", alpha=0.6, label="训练数据")
plt.plot(X_train, model.predict(X_train), color="red", linewidth=2, label="回归线")
plt.xlabel("特征 X")
plt.ylabel("目标值 y")
plt.title("线性回归 - 训练数据")
plt.legend()
plt.grid(True, alpha=0.3)

# 子图2：测试数据预测
plt.subplot(1, 2, 2)
plt.scatter(X_test, y_test, color="green", alpha=0.6, label="测试数据")
plt.scatter(X_test, y_pred, color="orange", alpha=0.8, label="预测值", marker="x")
for i in range(len(X_test)):
    plt.plot(
        [X_test[i], X_test[i]], [y_test[i], y_pred[i]], color="gray", alpha=0.3, linestyle="--"
    )
plt.xlabel("特征 X")
plt.ylabel("目标值 y")
plt.title("线性回归 - 测试数据预测")
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# 8. 使用模型进行新数据预测
print("\n新数据预测示例:")
new_X = np.array([[0.5], [1.0], [1.5], [2.0]])
predictions = model.predict(new_X)

for i, (x_val, pred) in enumerate(zip(new_X, predictions)):
    true_y = true_slope * x_val + true_intercept
    print(f"X = {x_val[0]:.1f}: 预测值 = {pred[0]:.4f}, 真实值 = {true_y[0]:.4f}")

# 9. 多特征线性回归示例（可选）
print("\n" + "=" * 50)
print("多特征线性回归示例")

# 生成多特征数据
n_samples_multi = 200
n_features = 3

X_multi = np.random.randn(n_samples_multi, n_features)
coefficients = np.array([2.5, -1.8, 0.7])
intercept_multi = 3.2
noise_multi = np.random.randn(n_samples_multi, 1) * 0.3

y_multi = X_multi @ coefficients.reshape(-1, 1) + intercept_multi + noise_multi

# 创建和训练多特征模型
model_multi = LinearRegression()
model_multi.fit(X_multi, y_multi)

print("\n多特征模型参数:")
print(f"学习到的系数: {model_multi.coef_[0]}")
print(f"真实系数: {coefficients}")
print(f"学习到的截距: {model_multi.intercept_[0]:.4f}")
print(f"真实截距: {intercept_multi}")

# 评估多特征模型
y_multi_pred = model_multi.predict(X_multi)
mse_multi = mean_squared_error(y_multi, y_multi_pred)
r2_multi = r2_score(y_multi, y_multi_pred)

print("\n多特征模型评估:")
print(f"均方误差 (MSE): {mse_multi:.4f}")
print(f"R² 分数: {r2_multi:.4f}")
