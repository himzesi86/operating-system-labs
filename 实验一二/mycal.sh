#!/bin/bash

# 月份名称映射数组
declare -A month_map=(
    ["january"]=1 ["jan"]=1 ["1"]=1
    ["february"]=2 ["feb"]=2 ["2"]=2
    ["march"]=3 ["mar"]=3 ["3"]=3
    ["april"]=4 ["apr"]=4 ["4"]=4
    ["may"]=5 ["5"]=5
    ["june"]=6 ["jun"]=6 ["6"]=6
    ["july"]=7 ["jul"]=7 ["7"]=7
    ["august"]=8 ["aug"]=8 ["8"]=8
    ["september"]=9 ["sep"]=9 ["9"]=9
    ["october"]=10 ["oct"]=10 ["10"]=10
    ["november"]=11 ["nov"]=11 ["11"]=11
    ["december"]=12 ["dec"]=12 ["12"]=12
)

# 月份名称显示
declare -A month_names=(
    ["1"]="January" ["2"]="February" ["3"]="March"
    ["4"]="April" ["5"]="May" ["6"]="June"
    ["7"]="July" ["8"]="August" ["9"]="September"
    ["10"]="October" ["11"]="November" ["12"]="December"
)

# 月份天数（非闰年）
declare -A month_days=(
    ["1"]=31 ["2"]=28 ["3"]=31 ["4"]=30 ["5"]=31 ["6"]=30
    ["7"]=31 ["8"]=31 ["9"]=30 ["10"]=31 ["11"]=30 ["12"]=31
)

# 显示用法
show_usage() {
    echo "用法: mycal [月份名|月份数字] 年"
    echo "示例: mycal October 2009"
    echo "       mycal 10 2009"
}

# 检查是否为闰年
is_leap_year() {
    local year=$1
    if (( year % 4 == 0 )); then
        if (( year % 100 == 0 )); then
            if (( year % 400 == 0 )); then
                return 0  # 是闰年
            else
                return 1  # 不是闰年
            fi
        else
            return 0  # 是闰年
        fi
    else
        return 1  # 不是闰年
    fi
}

# 计算某年某月第一天是星期几 (0=周日, 1=周一, ..., 6=周六)
# 使用Zeller一致性公式
get_first_day() {
    local month=$1
    local year=$2
    
    # Zeller公式需要1月和2月被视为前一年的13月和14月
    if (( month < 3 )); then
        month=$((month + 12))
        year=$((year - 1))
    fi
    
    local q=1  # 第一天
    local m=$month
    local k=$((year % 100))  # 年份后两位
    local j=$((year / 100))  # 世纪
    
    local h=$((q + 13*(m+1)/5 + k + k/4 + j/4 + 5*j))
    local day_of_week=$((h % 7))
    
    # 转换为0=周日, 1=周一, ..., 6=周六
    echo $(( (day_of_week + 6) % 7 ))
}

# 显示日历
display_calendar() {
    local month=$1
    local year=$2
    
    # 获取月份名称
    local month_name=${month_names[$month]}
    
    # 计算月份天数（考虑闰年）
    local days_in_month=${month_days[$month]}
    if (( month == 2 )); then
        if is_leap_year $year; then
            days_in_month=29
        else
            days_in_month=28
        fi
    fi
    
    # 获取第一天是星期几
    local first_day=$(get_first_day $month $year)
    
    # 打印标题
    echo
    echo "     $month_name $year"
    echo "Su Mo Tu We Th Fr Sa"
    
    # 打印首行缩进
    for ((i=0; i<first_day; i++)); do
        printf "   "
    done
    
    # 打印日期
    local current_day=$first_day
    for ((day=1; day<=days_in_month; day++)); do
        printf "%2d " $day
        current_day=$(( (current_day + 1) % 7 ))
        if (( current_day == 0 )); then
            echo
        fi
    done
    
    # 如果最后一行不满，换行
    if (( current_day != 0 )); then
        echo
    fi
    echo
}

# 主程序
main() {
    # 检查参数个数
    if [ $# -ne 2 ]; then
        echo "错误：参数数量不正确"
        show_usage
        exit 1
    fi
    
    local month_input=$1
    local year_input=$2
    
    # 转换为小写
    local month_lower=$(echo "$month_input" | tr '[:upper:]' '[:lower:]')
    
    # 验证月份
    if [ -z "${month_map[$month_lower]}" ]; then
        echo "错误：无效的月份 '$month_input'"
        show_usage
        exit 1
    fi
    
    local month=${month_map[$month_lower]}
    
    # 验证年份
    if ! [[ "$year_input" =~ ^[0-9]+$ ]] || [ "$year_input" -lt 1 ] || [ "$year_input" -gt 9999 ]; then
        echo "错误：无效的年份 '$year_input'，请输入1-9999之间的数字"
        exit 1
    fi
    
    # 显示日历
    display_calendar $month $year_input
}

# 运行主程序
main "$@"