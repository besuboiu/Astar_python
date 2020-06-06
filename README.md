# astar_python 
A*アルゴリズムをベースとして作成したコース探索アルゴリズムをMoon Board用に実装しました。
現状、クライミングにおいてはMoon Boardの課題が最も機械学習に向いていると思いますので、興味のある方のお役に少しでも立てますと幸いです。

A*-based course finding algorithm for Moon Board Implementation.
I think Moon Board is the most suitable for machine learning in climbing. I hope this will be of some help to those who are interested.

# DEMO
```
Please use letters and numbers and leave a space for each hold. Example: A12 B31
Enter a start hold
H5 F6
Enter a hold other than the start and goal
F8 D10 E13 C16 D4
Enter a goal hold
E18

--------------------  Start !  --------------------
Left Hand: F6, Right Hand: H5, Left Foot: D4, Right Foot: Foot Hold
Left Hand: F6, Right Hand: F8, Left Foot: D4, Right Foot: Foot Hold
Left Hand: F6, Right Hand: F8, Left Foot: D4, Right Foot: H5
Left Hand: D10, Right Hand: F8, Left Foot: D4, Right Foot: H5
Left Hand: D10, Right Hand: D10, Left Foot: D4, Right Foot: H5
Left Hand: D10, Right Hand: D10, Left Foot: D4, Right Foot: F6
Left Hand: D10, Right Hand: D10, Left Foot: F8, Right Foot: F6
Left Hand: D10, Right Hand: E13, Left Foot: F8, Right Foot: F6
Left Hand: E13, Right Hand: E13, Left Foot: F8, Right Foot: F6
Left Hand: E13, Right Hand: E13, Left Foot: F8, Right Foot: D10
Left Hand: E13, Right Hand: E13, Left Foot: C16, Right Foot: D10
Left Hand: E13, Right Hand: E18, Left Foot: C16, Right Foot: D10
Left Hand: E18, Right Hand: E18, Left Foot: C16, Right Foot: D10
--------------------  Goal !  ---------------------

```
 
# Usage
```bash
git clone https://github.com/besuboiu/astar_python
cd examples
python A\*_for_moon_board.py
```
 
# Note
入力は各ホールドをアルファベット（A〜K）+数字(1~18)で指定し、ホールドとホールドの間は必ずスペース開けてください。
To enter each hold, use letters (A to K) + numbers (1 to 18) and be sure to leave a space between holds.
 
# Author 
* 作成者 besuboiu
* E-mail n.n.n.h.h.b.b.26@gmail.com
