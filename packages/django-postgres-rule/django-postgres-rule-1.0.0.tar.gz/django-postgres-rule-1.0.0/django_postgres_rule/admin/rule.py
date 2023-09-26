from django.contrib import admin
from django.db import connection
from ..models import Rule

SQL = """
SELECT r.oid,c.relnamespace::regnamespace AS schemaname,
c.relname as tablename,
r.rulename,
case r.ev_type
 when '1' then 'SELECT'
 when '2' then 'UPDATE'
 when '3' then 'INSERT'
 when '4' then 'DELETE'
end as "event",
pg_catalog.pg_get_ruledef(r.oid, true) as definition
from pg_catalog.pg_rewrite r
  join pg_catalog.pg_class c on r.ev_class = c.oid
where
c.relnamespace::regnamespace::oid>=2200 AND
c.relnamespace::regnamespace::text NOT IN ('information_schema','pg_catalog') AND
r.rulename <> '_RETURN';
"""

class RuleAdmin(admin.ModelAdmin):
    list_display = [
        'oid',
        'schemaname',
        'tablename',
        'rulename',
        'event',
        'definition',
    ]
    list_filter = [
        'schemaname',
        'event',
    ]
    search_fields = [
        'schemaname',
        'tablename',
        'rulename',
        'event',
        'definition',
    ]

    def get_queryset(self, request):
        cursor = connection.cursor()
        cursor.execute(SQL)
        row_list = list(cursor.fetchall())
        rule_list = list(Rule.objects.all())
        oid_list = list(map(lambda r:r[0],row_list))
        oid2rule = {r.oid:r for r in rule_list}
        create_list = []
        for r in row_list:
            oid,schemaname,tablename,rulename,event,definition = r
            rule = oid2rule.get(oid,None)
            if not rule or rule.definition!=definition:
                create_list+=[Rule(
                    oid=oid,
                    schemaname=schemaname,
                    tablename=tablename,
                    rulename=rulename,
                    event=event,
                    definition=definition
                )]
        for rule in rule_list:
            if rule.oid not in oid_list:
                Rule.objects.filter(oid=rule.oid).delete()
        Rule.objects.bulk_create(create_list,
            update_conflicts=True,
            unique_fields = ['oid'],
            update_fields = [
                'schemaname',
                'tablename',
                'rulename',
                'event',
                'definition',
            ]
        )
        return super().get_queryset(request)

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(Rule,RuleAdmin)
