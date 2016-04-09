# estimate-adder
Evaluator for project time estimate expressions, such as `5w + 7d` (which would result in `1m 2w 2d`).

Supports the periods `d` (day), `w` (week), `m` (month) and `y` (year) and the operators `+` and `-`.

# Examples
```
$ ./estimate-adder.py 
> 5w + 7d
1m 2w 2d
> 6w
1m 2w
> 3d + 2d + 1w + 6d
3w 1d
> 9h
1d 1h
> 1y - 1h
11m 3w 4d 7h
> 8h
1d
> 5d
1w
> 4w
1m
> 12m
1y
> exit
Bye
```
