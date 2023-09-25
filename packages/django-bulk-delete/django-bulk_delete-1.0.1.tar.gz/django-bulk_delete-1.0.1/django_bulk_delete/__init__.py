
def bulk_delete(obj_list):
    model_list = list(set(map(lambda d:type(d),obj_list)))
    for model in sorted(model_list,key=lambda m:m._meta.db_table):
        model_obj_list = list(filter(lambda d:isinstance(d,model),obj_list))
        id_list = list(map(lambda d:d.id,model_obj_list))
        db_table = model._meta.db_table.replace('"','')
        print('DELETE: %s %s' % (db_table,len(model_obj_list)))
        model.objects.filter(id__in=id_list).delete()
