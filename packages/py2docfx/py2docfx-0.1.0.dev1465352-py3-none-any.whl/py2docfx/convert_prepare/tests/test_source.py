import os
import shutil

from py2docfx.convert_prepare.source import Source

def init_source(tmp_path):
    source_folder = os.path.join(tmp_path, "source_folder")
    os.mkdir(source_folder)
    yaml_output_folder = os.path.join(tmp_path, "yaml_output_folder")
    os.mkdir(yaml_output_folder)
    source = Source(source_folder=source_folder, yaml_output_folder=yaml_output_folder, package_name="dummy_package")
    return source

def test_copy_manual_rst(tmp_path):
    source = init_source(tmp_path)
    manual_rst_folder = os.path.join(tmp_path, "manual_rst_folder")
    shutil.copytree("convert_prepare/tests/data/source/manual_rst", manual_rst_folder)
    result = source.copy_manual_rst(manual_rst_folder)
    
    assert result
    assert os.path.exists(os.path.join(source.source_folder, "doc", "test.rst"))
    
def test_move_document_to_target(tmp_path):
    source = init_source(tmp_path)
    actual_doc_path = os.path.join(source.yaml_output_folder, "_build", "docfx_yaml")
    shutil.copytree("convert_prepare/tests/data/source/document", actual_doc_path)
    target_folder = os.path.join(tmp_path, "target_folder")
    source.move_document_to_target(target_folder)
    
    assert os.path.exists(os.path.join(target_folder, "dummy.yml"))