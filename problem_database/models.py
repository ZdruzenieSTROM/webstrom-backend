from django.db import models

# Create your models here.

class Seminar(models.Model):
    class Meta:
        verbose_name = 'seminár'
        verbose_name_plural = 'semináre'
    seminar_id = models.AutoField(verbose_name='id',default=1,primary_key=True)
    name = models.CharField(max_length=32,verbose_name='názov seminára')

    def __str__(self):
        return self.name


class ActivityType(models.Model):
    class Meta:
        verbose_name = 'typ aktivity'
        verbose_name_plural = 'typy aktivít'
    
    activity_type_id = models.AutoField(verbose_name='id',default=1,primary_key=True)
    name = models.CharField(verbose_name='názov',max_length=64)
    seminar_id = models.ForeignKey(Seminar,on_delete=models.CASCADE,verbose_name='seminár')

    def __str__(self):
        return self.name


class Activity(models.Model):
    class Meta:
        verbose_name = 'aktivita'
        verbose_name_plural = 'aktivity'
    
    activity_id = models.AutoField(verbose_name='id',default=1,primary_key=True)
    date = models.DateField(verbose_name='dátum')
    activity_type_id = models.ForeignKey(ActivityType,on_delete=models.CASCADE,verbose_name='typ aktivity')
    description = models.TextField(verbose_name='popis')
    soft_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.description


class Difficulty(models.Model):
    class Meta:
        verbose_name = 'náročnosť'
        verbose_name_plural = 'náročnosti'
    
    difficulty_id = models.AutoField(verbose_name='id',default=1,primary_key=True)
    name = models.CharField(verbose_name='názov',max_length=128)
    activity_type_id = models.ForeignKey(ActivityType,on_delete=models.CASCADE,verbose_name='typ aktivity')

    def __str__(self):
        return self.name


class Problem(models.Model):
    class Meta:
        verbose_name = 'príklad'
        verbose_name_plural = 'príklady'
    
    problem_id = models.AutoField(verbose_name='id',default=1,primary_key=True)
    problem = models.TextField(verbose_name='príklad')
    result = models.CharField(verbose_name='výsledok',max_length=128)
    solution = models.TextField(verbose_name='riešenie')
    #duplicate_problem_id = models.ForeignKey(self,on_delete=models.SET_DEFAULT,to_field=problem_id,verbose_name='duplikovaný príklad')
    soft_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.problem


class Media(models.Model):
    class Meta:
        verbose_name = 'súbor'
        verbose_name_plural = 'súbory'
    
    media_id = models.AutoField(verbose_name='id',default=1,primary_key=True)
    data = models.BinaryField(verbose_name='priložené súbory')
    problem_id = models.ForeignKey(Problem,on_delete=models.CASCADE,verbose_name='príklad')
    soft_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.data


class ProblemActivity(models.Model):
    class Meta:
        verbose_name = 'priradenie problému k aktivite/obtiežnosti'
        verbose_name_plural = 'priradenie problémov k aktivitám/obtiažnostiam'

    problem_id = models.ForeignKey(Problem,on_delete=models.CASCADE,verbose_name='príklad')
    activity_id = models.ForeignKey(Activity,on_delete=models.CASCADE,verbose_name='aktivita')
    difficulty_id = models.ForeignKey(Difficulty,on_delete=models.CASCADE,verbose_name='náročnosť')

    def __str__(self):
        return f'{ self.problem_id }, { self.activity_id }, { self.difficulty_id }'


class ProblemType(models.Model):
    class Meta:
        verbose_name = 'typ príkladu'
        verbose_name_plural = 'typy príkladov'

    problem_type_id = models.AutoField(verbose_name='id',default=1,primary_key=True)
    seminar_id = models.ForeignKey(Seminar,on_delete=models.CASCADE,verbose_name='seminár')
    name = models.CharField(verbose_name='názov',max_length=64)
    description = models.TextField(verbose_name='popis')

    def __str__(self):
        return self.name


class ProblemProblemType(models.Model):
    class Meta:
        verbose_name = 'priradenie príkladu k typu príkladu'
        verbose_name_plural = 'priradenia príkladov k typom príkladov'

    problem_id = models.ForeignKey(Problem,on_delete=models.CASCADE,verbose_name='príklad')
    problem_type_id = models.ForeignKey(ProblemType,on_delete=models.CASCADE,verbose_name='aktivita')

    def __str__(self):
        return f'{ self.problem_id }, { self.problem_type_id }'


class Tag(models.Model):
    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tagy'
    tag_id = models.AutoField(verbose_name='id',default=1,primary_key=True)
    name = models.CharField(max_length=64,verbose_name='názov tagu')

    def __str__(self):
        return self.name


class ProblemTag(models.Model):
    class Meta:
        verbose_name = 'priradenie príkladu k tagu'
        verbose_name_plural = 'priradenia príkladov k tagom'

    problem_id = models.ForeignKey(Problem,on_delete=models.CASCADE,verbose_name='príklad')
    tag_id = models.ForeignKey(Tag,on_delete=models.CASCADE,verbose_name='aktivita')

    def __str__(self):
        return f'{ self.problem_id }, { self.tag_id }'
