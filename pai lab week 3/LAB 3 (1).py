cap_x = int(input("Enter the capacity of X :"))
cap_y = int(input("Enter the capacity of Y :"))

x = 0
y = 0

print("1 FILL X TILL FULL")
print("2 FILL Y TILL FULL")
print("3 EMPTY X FULLY")
print("4 EMPTY Y FULLY")
print("5 POUR X INTO Y UNTILL X IS EMPTY")
print("6 POUR X INTO Y UNTILL Y IS FULL")
print("7 POUR Y INTO X UNTILL Y IS EMPTY")
print("8 POUR Y INTO X UNTILL X IS FULL")

choice = int(input("enter choice : "))

if choice == 1:
    x = cap_x

elif choice == 2:
    y = cap_y

elif choice == 3:
    x = 0

elif choice == 4:
    y = 0

elif choice == 5:
    y = y + x
    x = 0
    if y > cap_y:
        y = cap_y

elif choice == 6:
    space = cap_y - y
    if x <= space:
        y = y + x
        x = 0
    else:
        x = x - space
        y = cap_y

elif choice == 7:
    x = x + y
    y = 0
    if x > cap_x:
        x = cap_x

elif choice == 8:
    space = cap_x - x
    if y <= space:
        x = x + y
        y = 0
    else:
        y = y - space
        x = cap_x

print("x = ", x)
print("y = ", y)            

def solve_water_jug_dfs(cap_x, cap_y, target):

    stack = [(0, 0, [])]
    visited = set()

    while stack:
        x, y, path = stack.pop()
        if x == target or y == target:
            print("\n" + "="*30)
            print(f"TARGET ACHIEVED ({target}L)")
            print("="*30)
            for i, step in enumerate(path):
                print(f"Step {i+1}: {step}")
            return True

        if (x, y) in visited:
            continue
        visited.add((x, y))

        rules = [
            (cap_x, y, "FILL X TILL FULL (Rule 1)"),
            (x, cap_y, "FILL Y TILL FULL (Rule 2)"),
            (0, y, "EMPTY X FULLY (Rule 3)"),
            (x, 0, "EMPTY Y FULLY (Rule 4)"),
            (0, min(y + x, cap_y), "POUR X INTO Y (Rule 5/6)"), 
            (max(0, x - (cap_y - y)), cap_y, "POUR X INTO Y TILL Y FULL (Rule 6)"),
            (min(x + y, cap_x), 0, "POUR Y INTO X (Rule 7/8)"),
            (cap_x, max(0, y - (cap_x - x)), "POUR Y INTO X TILL X FULL (Rule 8)")
        ]

        for next_x, next_y, msg in rules:
            if (next_x, next_y) not in visited:
                new_path = path + [f"{msg} -> Current State: (X:{next_x}, Y:{next_y})"]
                stack.append((next_x, next_y, new_path))

    print("No solution found!")
    return False

target_amt = int(input("\nEnter target amount to achieve: "))
solve_water_jug_dfs(cap_x, cap_y, target_amt)