from django.db import models

# Create your models here.

class Seminar(models.Model):
    class Meta:
        verbose_name = 'seminár'
        verbose_name_plural = 'semináre'
    
    name = models.CharField(max_length=32,verbose_name='názov seminára')

    def __str__(self):
        return self.name


class ActivityType(models.Model):
    class Meta:
        verbose_name = 'typ aktivity'
        verbose_name_plural = 'typy aktivít'
    
    name = models.CharField(verbose_name='názov',max_length=64)
    seminar = models.ForeignKey(Seminar,default=1,on_delete=models.CASCADE,verbose_name='seminár')

    def __str__(self):
        return self.name


class Activity(models.Model):
    class Meta:
        verbose_name = 'aktivita'
        verbose_name_plural = 'aktivity'
    
    #dátum je vo formáte YYYY-MM-DD
    date = models.DateField(verbose_name='dátum')
    activity_type = models.ForeignKey(ActivityType,default=1,on_delete=models.CASCADE,verbose_name='typ aktivity')
    description = models.TextField(verbose_name='popis')
    soft_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.description


class Difficulty(models.Model):
    class Meta:
        verbose_name = 'náročnosť'
        verbose_name_plural = 'náročnosti'
    
    name = models.CharField(verbose_name='názov',max_length=128)
    activity_type = models.ForeignKey(ActivityType,default=1,on_delete=models.CASCADE,verbose_name='typ aktivity')

    def __str__(self):
        return self.name


class ProblemType(models.Model):
    class Meta:
        verbose_name = 'typ príkladu'
        verbose_name_plural = 'typy príkladov'

    seminar = models.ForeignKey(Seminar,default=1,on_delete=models.CASCADE,verbose_name='seminár')
    name = models.CharField(verbose_name='názov',max_length=64)
    description = models.TextField(verbose_name='popis')

    def __str__(self):
        return self.name


class Problem(models.Model):
    class Meta:
        verbose_name = 'príklad'
        verbose_name_plural = 'príklady'
    
    problem = models.TextField(verbose_name='príklad')
    result = models.CharField(verbose_name='výsledok',max_length=128)
    solution = models.TextField(verbose_name='riešenie')
    #duplicate_problem_id = models.ForeignKey(self,on_delete=models.SET_DEFAULT,to_field=problem_id,verbose_name='duplikovaný príklad')
    soft_deleted = models.BooleanField(default=False)
    problem_type = models.ManyToManyField(ProblemType)

    def __str__(self):
        return self.problem


class Media(models.Model):
    class Meta:
        verbose_name = 'súbor'
        verbose_name_plural = 'súbory'
    
    data = models.BinaryField(verbose_name='priložené súbory')
    problem = models.ForeignKey(Problem,default=1,on_delete=models.CASCADE,verbose_name='príklad')
    soft_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.data


class ProblemActivity(models.Model):
    class Meta:
        verbose_name = 'priradenie problému k aktivite/obtiežnosti'
        verbose_name_plural = 'priradenie problémov k aktivitám/obtiažnostiam'

    problem = models.ForeignKey(Problem,default=1,on_delete=models.CASCADE,verbose_name='príklad')
    activity = models.ForeignKey(Activity,default=1,on_delete=models.CASCADE,verbose_name='aktivita')
    difficulty = models.ForeignKey(Difficulty,default=1,on_delete=models.CASCADE,verbose_name='náročnosť')

    def __str__(self):
        return f'{ self.problem_id }, { self.activity_id }, { self.difficulty_id }'


class Tag(models.Model):
    class Meta:
        verbose_name = 'tag'
        verbose_name_plural = 'tagy'
    name = models.CharField(max_length=64,verbose_name='názov tagu')

    def __str__(self):
        return self.name


class ProblemTag(models.Model):
    class Meta:
        verbose_name = 'priradenie príkladu k tagu'
        verbose_name_plural = 'priradenia príkladov k tagom'

    problem = models.ForeignKey(Problem,default=1,on_delete=models.CASCADE,verbose_name='príklad')
    tag = models.ForeignKey(Tag,default=1,on_delete=models.CASCADE,verbose_name='aktivita')

    def __str__(self):
        return f'{ self.problem_id }, { self.tag_id }'
