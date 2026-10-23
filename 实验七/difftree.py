#!/usr/bin/env python3 

import os
import sys
import hashlib
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class FileInfo:
    """文件信息类"""
    def __init__(self, path, rel_path):
        self.path = path
        self.rel_path = rel_path
        self.name = path.name
        self.is_dir = path.is_dir()
        self.is_file = path.is_file()
        self.size = path.stat().st_size if not path.is_dir() else 0
        self.mtime = datetime.fromtimestamp(path.stat().st_mtime)
        
        # 计算文件哈希（如果是文件）
        self.hash = self._calculate_hash() if path.is_file() else None
    
    def _calculate_hash(self):
        """计算文件的MD5哈希值"""
        try:
            hasher = hashlib.md5()
            with open(self.path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except (IOError, OSError):
            return None
    
    def __eq__(self, other):
        """比较两个文件是否相同"""
        if self.is_dir != other.is_dir:
            return False
        if self.is_file:
            # 首先比较大小，如果大小不同则内容肯定不同
            if self.size != other.size:
                return False
            # 大小相同的情况下比较哈希
            return self.hash == other.hash
        # 目录只需要类型相同就认为相等
        return True
    
    def __str__(self):
        file_type = "DIR" if self.is_dir else "FILE"
        return f"{file_type} {self.rel_path} ({self.size} bytes, {self.mtime})"

class DirectoryTree:
    """目录树类"""
    def __init__(self, root_path):
        self.root = Path(root_path).resolve()
        self.files = {}  # 相对路径 -> FileInfo
        self.dirs = set()  # 存储所有目录的相对路径
        self._build_tree()
    
    def _build_tree(self, current_path=None, rel_path=""):
        """递归构建目录树"""
        if current_path is None:
            current_path = self.root
        
        # 将当前目录添加到目录集合中
        if rel_path:  # 不添加根目录（空路径）
            self.dirs.add(rel_path)
        
        try:
            for item in current_path.iterdir():
                # 跳过隐藏文件（可选）
                if item.name.startswith('.'):
                    continue
                
                item_rel_path = os.path.join(rel_path, item.name)
                file_info = FileInfo(item, item_rel_path)
                self.files[item_rel_path] = file_info
                
                # 如果是目录，递归处理
                if item.is_dir():
                    self._build_tree(item, item_rel_path)
        except PermissionError:
            print(f"警告: 无权限访问目录 {current_path}", file=sys.stderr)

class DiffTree:
    """目录比较器 - 修正统计bug"""
    def __init__(self, dir1, dir2):
        self.tree1 = DirectoryTree(dir1)
        self.tree2 = DirectoryTree(dir2)
        self.differences = []
    
    def compare(self):
        """比较两个目录树"""
        # 比较所有文件和目录
        all_paths = set(self.tree1.files.keys()) | set(self.tree2.files.keys())
        
        for path in sorted(all_paths):
            file1 = self.tree1.files.get(path)
            file2 = self.tree2.files.get(path)
            
            if file1 is None:
                self.differences.append(("+", path, "只在第二个目录中存在", file2.is_dir))
            elif file2 is None:
                self.differences.append(("-", path, "只在第一个目录中存在", file1.is_dir))
            elif not file1 == file2:
                if file1.is_dir != file2.is_dir:
                    self.differences.append(("*", path, "类型不同（文件/目录）", file1.is_dir))
                elif file1.is_file:
                    if file1.size != file2.size:
                        self.differences.append(("*", path, f"大小不同: {file1.size} vs {file2.size}", False))
                    elif file1.hash != file2.hash:
                        self.differences.append(("*", path, "内容不同（哈希值不匹配）", False))
        
        # 比较目录结构（空目录）
        all_dirs = self.tree1.dirs | self.tree2.dirs
        for dir_path in sorted(all_dirs):
            if dir_path not in self.tree1.dirs:
                # 检查是否已经有该目录下的文件被报告
                has_children_reported = any(path.startswith(dir_path + os.sep) for _, path, _, _ in self.differences)
                if not has_children_reported:
                    self.differences.append(("+", dir_path, "空目录（只在第二个目录中存在）", True))
            elif dir_path not in self.tree2.dirs:
                has_children_reported = any(path.startswith(dir_path + os.sep) for _, path, _, _ in self.differences)
                if not has_children_reported:
                    self.differences.append(("-", dir_path, "空目录（只在第一个目录中存在）", True))
    
    def print_report(self):
        """打印比较报告"""
        if not self.differences:
            print("两个目录完全相同")
            return
        
        print(f"目录比较报告: {self.tree1.root} vs {self.tree2.root}")
        print("=" * 60)
        
        # 按路径深度排序，使输出更有层次感
        sorted_diffs = sorted(self.differences, key=lambda x: (x[1].count(os.sep), x[1]))
        
        for diff_type, path, description, is_dir in sorted_diffs:
            prefix = "DIR " if is_dir else "FILE"
            if diff_type == "-":
                print(f"[-] {prefix} {path} - {description}")
            elif diff_type == "+":
                print(f"[+] {prefix} {path} - {description}")
            elif diff_type == "*":
                print(f"[*] {prefix} {path} - {description}")
        
        # 修正统计信息
        stats = {
            'missing_files': 0,
            'missing_dirs': 0,
            'extra_files': 0,
            'extra_dirs': 0,
            'different_files': 0,
            'different_dirs': 0
        }
        
        for diff_type, path, description, is_dir in self.differences:
            if diff_type == "-":
                if is_dir:
                    stats['missing_dirs'] += 1
                else:
                    stats['missing_files'] += 1
            elif diff_type == "+":
                if is_dir:
                    stats['extra_dirs'] += 1
                else:
                    stats['extra_files'] += 1
            elif diff_type == "*":
                if is_dir:
                    stats['different_dirs'] += 1
                else:
                    stats['different_files'] += 1
        
        print("=" * 60)
        print(f"统计信息:")
        print(f"  缺失: {stats['missing_files'] + stats['missing_dirs']} (文件: {stats['missing_files']}, 目录: {stats['missing_dirs']})")
        print(f"  额外: {stats['extra_files'] + stats['extra_dirs']} (文件: {stats['extra_files']}, 目录: {stats['extra_dirs']})")
        print(f"  不同: {stats['different_files'] + stats['different_dirs']} (文件: {stats['different_files']}, 目录: {stats['different_dirs']})")
        print(f"  总计差异: {len(self.differences)} 项")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='比较两个目录的文件结构和内容')
    parser.add_argument('dir1', help='第一个目录路径')
    parser.add_argument('dir2', help='第二个目录路径')
    parser.add_argument('--ignore-hidden', action='store_true', 
                       help='忽略隐藏文件（以.开头的文件）')
    parser.add_argument('--brief', action='store_true',
                       help='简要模式，只显示是否有差异')
    
    args = parser.parse_args()
    
    # 检查目录是否存在
    if not os.path.isdir(args.dir1):
        print(f"错误: 目录 '{args.dir1}' 不存在")
        sys.exit(1)
    
    if not os.path.isdir(args.dir2):
        print(f"错误: 目录 '{args.dir2}' 不存在")
        sys.exit(1)
    
    # 比较目录
    differ = DiffTree(args.dir1, args.dir2)
    differ.compare()
    
    if args.brief:
        # 简要模式
        if differ.differences:
            print("目录存在差异")
            sys.exit(1)
        else:
            print("目录相同")
            sys.exit(0)
    else:
        differ.print_report()

if __name__ == "__main__":
    main()
