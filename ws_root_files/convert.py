import pandas as pd

# 파일 경로
input_csv = '~/ws/waypoint.csv'     # 원본 CSV 파일명
output_csv = '~/ws/wapoint_to_slam.csv'  # 변환 결과 저장할 파일명

# offset (map - ego)
offset_x = -19.0-(-0.19691)
offset_y = 4.5 - (-0.278991)
offset_z = -0.03

# CSV 읽기
df = pd.read_csv(input_csv)

# 컬럼 이름은 실제 파일에 맞게 수정 필요
# 예: 'x', 'y', 'z' 또는 'position.x' 등
# 여기서는 'x', 'y', 'z'라고 가정
df['field.position.x'] = df['field.position.x'] - offset_x
df['field.position.y'] = df['field.position.y'] - offset_y
df['field.position.z'] = df['field.position.z'] - offset_z

# 결과 CSV 저장
df.to_csv(output_csv, index=False)

print(f"Corrected positions saved to {output_csv}")
